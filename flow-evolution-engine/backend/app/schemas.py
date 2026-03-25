from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    text: str
    chars: int


class GenerateVariantsRequest(BaseModel):
    text: str
    name: str = "HyperAgent Flow"
    version_group: str = "v1"
    variant_count: int = Field(default=3, ge=2, le=6)


class ScenarioRequest(BaseModel):
    scenario: str
    version_group: str


class SelectWinnersRequest(BaseModel):
    version_group: str
    top_k: int = Field(default=2, ge=1, le=5)


class EvolveWinnersRequest(BaseModel):
    version_group: str
    top_k: int = Field(default=2, ge=1, le=5)
    next_version_group: str
    children_per_winner: int = Field(default=3, ge=2, le=6)


class FlowOut(BaseModel):
    id: int
    name: str
    version_group: str
    variant_id: str
    parent_id: Optional[int]
    mutation_type: Optional[str]
    score: float
    flow_json: Dict[str, Any]
    created_at: datetime


class CompetitionExecutionItem(BaseModel):
    flow_id: int
    version_group: str
    variant_id: str
    execution_id: int
    path: List[str]
    trace: List[Dict[str, Any]]
    output_text: str


class CompetitionEvaluationItem(BaseModel):
    flow_id: int
    version_group: str
    variant_id: str
    score: float
    signals: Dict[str, Any]
    notes: str


class RunCompetitionResponse(BaseModel):
    executions: List[CompetitionExecutionItem]
    evaluations: List[CompetitionEvaluationItem]


class WinnerOut(BaseModel):
    flow_id: int
    version_group: str
    variant_id: str
    score: float


class EvolutionHistoryOut(BaseModel):
    id: int
    parent_flow: int
    child_flow: int
    mutation_type: str
    performance_delta: float
    created_at: datetime


class MutationInsight(BaseModel):
    mutation_type: str
    avg_delta: float
    uses: int
