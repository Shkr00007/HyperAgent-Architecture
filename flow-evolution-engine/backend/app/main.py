import json
import string
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import EvaluationLog, EvolutionHistory, ExecutionLog, Flow
from .schemas import (
    EvolveWinnersRequest,
    EvolutionHistoryOut,
    FlowOut,
    GenerateVariantsRequest,
    IngestResponse,
    MutationInsight,
    RunCompetitionResponse,
    ScenarioRequest,
    SelectWinnersRequest,
    WinnerOut,
)
from .services.evaluation_engine import evaluate_execution
from .services.evolution_engine import build_mutation_guidance, mutation_insights, select_top_flows
from .services.execution_engine import execute_flow
from .services.extraction_service import generate_flow_variants, mutate_winner_variants
from .services.ingestion_service import extract_text_from_pdf

Base.metadata.create_all(bind=engine)

app = FastAPI(title="HyperAgent Flow Evolution System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def to_flow_out(flow: Flow) -> FlowOut:
    return FlowOut(
        id=flow.id,
        name=flow.name,
        version_group=flow.version_group,
        variant_id=flow.variant_id,
        parent_id=flow.parent_id,
        mutation_type=flow.mutation_type,
        score=flow.score,
        flow_json=json.loads(flow.flow_json),
        created_at=flow.created_at,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(None), text: str = Form(default="")):
    if file:
        content = await file.read()
        extracted = extract_text_from_pdf(content) if file.filename.lower().endswith(".pdf") else content.decode("utf-8", errors="ignore")
    else:
        extracted = text

    if not extracted.strip():
        raise HTTPException(status_code=400, detail="No text content found")
    return IngestResponse(text=extracted, chars=len(extracted))


@app.post("/generate-variants", response_model=list[FlowOut])
def generate_variants(payload: GenerateVariantsRequest, db: Session = Depends(get_db)):
    variants = generate_flow_variants(payload.text, payload.variant_count)
    created = []
    for i, flow_json in enumerate(variants):
        variant_label = string.ascii_lowercase[i]
        flow = Flow(
            name=payload.name,
            source_text=payload.text,
            flow_json=json.dumps(flow_json),
            version_group=payload.version_group,
            variant_id=variant_label,
        )
        db.add(flow)
        created.append(flow)

    db.commit()
    for f in created:
        db.refresh(f)
    return [to_flow_out(f) for f in created]


@app.post("/run-competition", response_model=RunCompetitionResponse)
def run_competition(payload: ScenarioRequest, db: Session = Depends(get_db)):
    flows = db.query(Flow).filter(Flow.version_group == payload.version_group).all()
    if not flows:
        raise HTTPException(status_code=404, detail="No flow variants in this version group")

    executions = []
    evaluations = []

    for flow in flows:
        fjson = json.loads(flow.flow_json)
        run = execute_flow(fjson, payload.scenario)
        ex = ExecutionLog(
            flow_id=flow.id,
            scenario=payload.scenario,
            trace_json=json.dumps({"path": run["path"], "trace": run["trace"]}),
            output_text=run["output_text"],
        )
        db.add(ex)
        db.commit()
        db.refresh(ex)

        scored = evaluate_execution(fjson, run, payload.scenario)
        flow.score = scored["score"]
        ev = EvaluationLog(
            flow_id=flow.id,
            execution_id=ex.id,
            score=scored["score"],
            signals_json=json.dumps(scored["signals"]),
            notes=scored["notes"],
        )
        db.add(ev)
        db.commit()

        executions.append(
            {
                "flow_id": flow.id,
                "version_group": flow.version_group,
                "variant_id": flow.variant_id,
                "execution_id": ex.id,
                "path": run["path"],
                "trace": run["trace"],
                "output_text": run["output_text"],
            }
        )
        evaluations.append(
            {
                "flow_id": flow.id,
                "version_group": flow.version_group,
                "variant_id": flow.variant_id,
                "score": scored["score"],
                "signals": scored["signals"],
                "notes": scored["notes"],
            }
        )

    db.commit()
    return {"executions": executions, "evaluations": evaluations}


@app.post("/select-winners", response_model=list[WinnerOut])
def select_winners(payload: SelectWinnersRequest, db: Session = Depends(get_db)):
    flows = db.query(Flow).filter(Flow.version_group == payload.version_group).all()
    if not flows:
        raise HTTPException(status_code=404, detail="No flows in this version group")

    scored = [{"flow_id": f.id, "version_group": f.version_group, "variant_id": f.variant_id, "score": f.score} for f in flows]
    return select_top_flows(scored, payload.top_k)


@app.post("/evolve-winners", response_model=list[FlowOut])
def evolve_winners(payload: EvolveWinnersRequest, db: Session = Depends(get_db)):
    parent_candidates = select_winners(SelectWinnersRequest(version_group=payload.version_group, top_k=payload.top_k), db)

    history_rows = [
        {"mutation_type": h.mutation_type, "performance_delta": h.performance_delta}
        for h in db.query(EvolutionHistory).all()
    ]
    guidance = build_mutation_guidance(mutation_insights(history_rows))

    children_created = []
    idx = 0
    for winner in parent_candidates:
        parent = db.query(Flow).filter(Flow.id == winner.flow_id).first()
        parent_flow_json = json.loads(parent.flow_json)
        children = mutate_winner_variants(parent_flow_json, guidance, payload.children_per_winner)

        for child in children:
            idx += 1
            variant_id = f"{parent.variant_id}{idx}"
            mutation_type = child.get("mutation_type", child.get("strategy", "mutation"))
            cf = Flow(
                name=parent.name,
                source_text=parent.source_text,
                flow_json=json.dumps(child),
                version_group=payload.next_version_group,
                variant_id=variant_id,
                parent_id=parent.id,
                mutation_type=mutation_type,
                score=0.0,
            )
            db.add(cf)
            db.commit()
            db.refresh(cf)

            eh = EvolutionHistory(
                parent_flow=parent.id,
                child_flow=cf.id,
                mutation_type=mutation_type,
                performance_delta=0.0,
            )
            db.add(eh)
            db.commit()

            children_created.append(cf)

    return [to_flow_out(c) for c in children_created]


@app.get("/flows", response_model=list[FlowOut])
def list_flows(db: Session = Depends(get_db)):
    return [to_flow_out(f) for f in db.query(Flow).order_by(Flow.created_at.desc()).all()]


@app.get("/flows/{version_group}", response_model=list[FlowOut])
def list_flows_by_group(version_group: str, db: Session = Depends(get_db)):
    return [to_flow_out(f) for f in db.query(Flow).filter(Flow.version_group == version_group).order_by(Flow.score.desc()).all()]


@app.get("/best-flow", response_model=FlowOut)
def best_flow(db: Session = Depends(get_db)):
    flow = db.query(Flow).order_by(Flow.score.desc(), Flow.created_at.desc()).first()
    if not flow:
        raise HTTPException(status_code=404, detail="No flows available")
    return to_flow_out(flow)


@app.get("/evolution-history", response_model=list[EvolutionHistoryOut])
def evolution_history(db: Session = Depends(get_db)):
    return db.query(EvolutionHistory).order_by(EvolutionHistory.created_at.asc()).all()


@app.get("/mutation-insights", response_model=list[MutationInsight])
def get_mutation_insights(db: Session = Depends(get_db)):
    rows = [{"mutation_type": r.mutation_type, "performance_delta": r.performance_delta} for r in db.query(EvolutionHistory).all()]
    return mutation_insights(rows)
