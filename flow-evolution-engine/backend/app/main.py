import json
import string
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import EvaluationLog, EvolutionHistory, ExecutionLog, Flow, MetaLearning
from .schemas import (
    EvolveWinnersRequest,
    EvolutionHistoryOut,
    FlowOut,
    GenerateVariantsRequest,
    IngestResponse,
    MetaLearningOut,
    MutationInsight,
    RunCompetitionResponse,
    ScenarioRequest,
    SelectWinnersRequest,
    WinnerOut,
)
from .services.evaluation_engine import evaluate_execution
from .services.evolution_engine import build_meta_bias, mutation_insights, select_top_flows, summarize_structure_patterns
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


def refresh_meta_learning(db: Session):
    mutation_types = [m[0] for m in db.query(Flow.mutation_type).filter(Flow.mutation_type.isnot(None)).distinct().all()]
    for mtype in mutation_types:
        flows = db.query(Flow).filter(Flow.mutation_type == mtype).all()
        if not flows:
            continue
        scores = [f.score for f in flows]
        avg_score = sum(scores) / len(scores)
        success_threshold = 0.6
        wins = sum(1 for s in scores if s >= success_threshold)
        trials = len(scores)
        success_rate = wins / trials if trials else 0.0

        row = db.query(MetaLearning).filter(MetaLearning.mutation_type == mtype).first()
        if not row:
            row = MetaLearning(mutation_type=mtype)
            db.add(row)
        row.avg_score = round(avg_score, 4)
        row.success_rate = round(success_rate, 4)
        row.wins = wins
        row.trials = trials
    db.commit()


def strict_select_and_discard(db: Session, version_group: str, top_k: int) -> list[dict]:
    flows = db.query(Flow).filter(Flow.version_group == version_group).all()
    scored = [{"flow_id": f.id, "version_group": f.version_group, "variant_id": f.variant_id, "score": f.score} for f in flows]
    winners = select_top_flows(scored, top_k)
    winner_ids = {w["flow_id"] for w in winners}

    losers = [f for f in flows if f.id not in winner_ids]
    for loser in losers:
        db.query(ExecutionLog).filter(ExecutionLog.flow_id == loser.id).delete()
        db.query(EvaluationLog).filter(EvaluationLog.flow_id == loser.id).delete()
        db.query(Flow).filter(Flow.id == loser.id).delete()
    db.commit()
    return winners


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
        flow = Flow(
            name=payload.name,
            source_text=payload.text,
            flow_json=json.dumps(flow_json),
            version_group=payload.version_group,
            variant_id=string.ascii_lowercase[i],
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

    executions, evaluations = [], []

    for flow in flows:
        fjson = json.loads(flow.flow_json)
        run = execute_flow(fjson, payload.scenario)
        ex = ExecutionLog(flow_id=flow.id, scenario=payload.scenario, trace_json=json.dumps({"path": run["path"], "trace": run["trace"]}), output_text=run["output_text"])
        db.add(ex)
        db.commit()
        db.refresh(ex)

        scored = evaluate_execution(fjson, run, payload.scenario)
        flow.score = scored["score"]
        db.add(EvaluationLog(flow_id=flow.id, execution_id=ex.id, score=scored["score"], signals_json=json.dumps(scored["signals"]), notes=scored["notes"]))

        if flow.parent_id:
            parent = db.query(Flow).filter(Flow.id == flow.parent_id).first()
            link = db.query(EvolutionHistory).filter(EvolutionHistory.child_flow == flow.id).first()
            if parent and link:
                link.performance_delta = round(flow.score - parent.score, 4)

        executions.append({
            "flow_id": flow.id,
            "version_group": flow.version_group,
            "variant_id": flow.variant_id,
            "execution_id": ex.id,
            "path": run["path"],
            "trace": run["trace"],
            "output_text": run["output_text"],
        })
        evaluations.append({
            "flow_id": flow.id,
            "version_group": flow.version_group,
            "variant_id": flow.variant_id,
            "score": scored["score"],
            "signals": scored["signals"],
            "notes": scored["notes"],
        })

    db.commit()
    refresh_meta_learning(db)
    return {"executions": executions, "evaluations": evaluations}


@app.post("/select-winners", response_model=list[WinnerOut])
def select_winners(payload: SelectWinnersRequest, db: Session = Depends(get_db)):
    flows = db.query(Flow).filter(Flow.version_group == payload.version_group).all()
    if not flows:
        raise HTTPException(status_code=404, detail="No flows in this version group")
    return strict_select_and_discard(db, payload.version_group, payload.top_k)


@app.post("/evolve-winners", response_model=list[FlowOut])
def evolve_winners(payload: EvolveWinnersRequest, db: Session = Depends(get_db)):
    winners = strict_select_and_discard(db, payload.version_group, payload.top_k)

    meta_rows = [{
        "mutation_type": m.mutation_type,
        "avg_score": m.avg_score,
        "success_rate": m.success_rate,
    } for m in db.query(MetaLearning).all()]
    winner_flows = [json.loads(db.query(Flow).filter(Flow.id == w["flow_id"]).first().flow_json) for w in winners]
    meta_bias = build_meta_bias(meta_rows)
    structure_bias = summarize_structure_patterns(winner_flows)
    prompt_bias = f"{meta_bias}; {structure_bias}"

    children_created = []
    for winner in winners:
        parent = db.query(Flow).filter(Flow.id == winner["flow_id"]).first()
        parent_flow_json = json.loads(parent.flow_json)
        children = mutate_winner_variants(parent_flow_json, prompt_bias)

        for idx, child in enumerate(children, start=1):
            mutation_type = child.get("mutation_type", "hybrid")
            cf = Flow(
                name=parent.name,
                source_text=parent.source_text,
                flow_json=json.dumps(child),
                version_group=payload.next_version_group,
                variant_id=f"{parent.variant_id}{idx}",
                parent_id=parent.id,
                mutation_type=mutation_type,
                score=0.0,
            )
            db.add(cf)
            db.commit()
            db.refresh(cf)
            db.add(EvolutionHistory(parent_flow=parent.id, child_flow=cf.id, mutation_type=mutation_type, performance_delta=0.0))
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


@app.get("/meta-learning", response_model=list[MetaLearningOut])
def get_meta_learning(db: Session = Depends(get_db)):
    return db.query(MetaLearning).order_by(MetaLearning.success_rate.desc(), MetaLearning.avg_score.desc()).all()
