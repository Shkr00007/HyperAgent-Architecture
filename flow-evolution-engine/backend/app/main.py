import json
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import EvaluationLog, EvolutionLog, ExecutionLog, Flow
from .schemas import (
    EvaluateRequest,
    EvaluateResponse,
    EvolutionItem,
    EvolveRequest,
    ExecuteFlowRequest,
    ExecuteFlowResponse,
    ExtractFlowRequest,
    FlowOut,
    IngestResponse,
)
from .services.evaluation_engine import evaluate_execution
from .services.evolution_engine import evolve_flow
from .services.execution_engine import execute_flow
from .services.extraction_service import extract_flow_from_text
from .services.ingestion_service import extract_text_from_pdf

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flow Evolution Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(None), text: str = Form(default="")):
    if file:
        content = await file.read()
        if file.filename.lower().endswith(".pdf"):
            extracted = extract_text_from_pdf(content)
        else:
            extracted = content.decode("utf-8", errors="ignore")
    else:
        extracted = text

    if not extracted.strip():
        raise HTTPException(status_code=400, detail="No text content found")

    return IngestResponse(text=extracted, chars=len(extracted))


@app.post("/extract-flow", response_model=FlowOut)
def extract_flow(payload: ExtractFlowRequest, db: Session = Depends(get_db)):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    flow_json = extract_flow_from_text(payload.text)
    db_flow = Flow(name=payload.name, source_text=payload.text, flow_json=json.dumps(flow_json), version=1)
    db.add(db_flow)
    db.commit()
    db.refresh(db_flow)

    return FlowOut(
        id=db_flow.id,
        name=db_flow.name,
        version=db_flow.version,
        score=db_flow.score,
        parent_flow_id=db_flow.parent_flow_id,
        flow_json=flow_json,
        created_at=db_flow.created_at,
    )


@app.post("/execute-flow", response_model=ExecuteFlowResponse)
def execute_flow_endpoint(payload: ExecuteFlowRequest, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == payload.flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    flow_json = json.loads(flow.flow_json)
    result = execute_flow(flow_json, payload.scenario)

    execution = ExecutionLog(flow_id=flow.id, scenario=payload.scenario, output_json=json.dumps(result))
    db.add(execution)
    db.commit()
    db.refresh(execution)

    return ExecuteFlowResponse(execution_id=execution.id, **result)


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == payload.flow_id).first()
    execution = db.query(ExecutionLog).filter(ExecutionLog.id == payload.execution_id).first()
    if not flow or not execution:
        raise HTTPException(status_code=404, detail="Flow or execution not found")

    flow_json = json.loads(flow.flow_json)
    execution_json = json.loads(execution.output_json)
    scored = evaluate_execution(flow_json, execution_json)

    flow.score = scored["score"]
    elog = EvaluationLog(
        flow_id=flow.id,
        execution_id=execution.id,
        score=scored["score"],
        notes=scored["notes"],
    )
    db.add(elog)
    db.commit()

    return EvaluateResponse(**scored)


@app.post("/evolve", response_model=FlowOut)
def evolve(payload: EvolveRequest, db: Session = Depends(get_db)):
    flow = db.query(Flow).filter(Flow.id == payload.flow_id).first()
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    current_flow = json.loads(flow.flow_json)
    evolved = evolve_flow(current_flow, flow.score)

    new_flow = Flow(
        name=flow.name,
        source_text=flow.source_text,
        flow_json=json.dumps(evolved["flow"]),
        version=flow.version + 1,
        parent_flow_id=flow.id,
        score=min(flow.score + 0.05, 1.0),
    )
    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)

    log = EvolutionLog(
        old_flow_id=flow.id,
        new_flow_id=new_flow.id,
        reason=evolved["reason"],
        old_score=flow.score,
        new_score=new_flow.score,
    )
    db.add(log)
    db.commit()

    return FlowOut(
        id=new_flow.id,
        name=new_flow.name,
        version=new_flow.version,
        score=new_flow.score,
        parent_flow_id=new_flow.parent_flow_id,
        flow_json=evolved["flow"],
        created_at=new_flow.created_at,
    )


@app.get("/flows", response_model=list[FlowOut])
def list_flows(db: Session = Depends(get_db)):
    flows = db.query(Flow).order_by(Flow.created_at.desc()).all()
    return [
        FlowOut(
            id=f.id,
            name=f.name,
            version=f.version,
            score=f.score,
            parent_flow_id=f.parent_flow_id,
            flow_json=json.loads(f.flow_json),
            created_at=f.created_at,
        )
        for f in flows
    ]


@app.get("/best-flow", response_model=FlowOut)
def best_flow(db: Session = Depends(get_db)):
    flow = db.query(Flow).order_by(Flow.score.desc(), Flow.created_at.desc()).first()
    if not flow:
        raise HTTPException(status_code=404, detail="No flows available")
    return FlowOut(
        id=flow.id,
        name=flow.name,
        version=flow.version,
        score=flow.score,
        parent_flow_id=flow.parent_flow_id,
        flow_json=json.loads(flow.flow_json),
        created_at=flow.created_at,
    )


@app.get("/evolution-log", response_model=list[EvolutionItem])
def evolution_log(db: Session = Depends(get_db)):
    logs = db.query(EvolutionLog).order_by(EvolutionLog.created_at.asc()).all()
    return logs
