from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    text: str
    chars: int


class ExtractFlowRequest(BaseModel):
    text: Optional[str] = None
    name: str = "Untitled Flow"


class FlowNode(BaseModel):
    id: str
    type: str = "action"
    label: str
    details: Optional[str] = None


class FlowEdge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None


class FlowData(BaseModel):
    nodes: List[FlowNode]
    edges: List[FlowEdge]
    entry_node: str


class FlowOut(BaseModel):
    id: int
    name: str
    version: int
    score: float
    parent_flow_id: Optional[int]
    flow_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ExecuteFlowRequest(BaseModel):
    flow_id: int
    scenario: str


class ExecuteFlowResponse(BaseModel):
    execution_id: int
    path: List[str]
    trace: List[Dict[str, Any]]
    final_output: str


class EvaluateRequest(BaseModel):
    flow_id: int
    execution_id: int


class EvaluateResponse(BaseModel):
    score: float = Field(..., ge=0, le=1)
    notes: str


class EvolveRequest(BaseModel):
    flow_id: int


class EvolutionItem(BaseModel):
    id: int
    old_flow_id: int
    new_flow_id: int
    reason: str
    old_score: float
    new_score: float
    created_at: datetime

    class Config:
        from_attributes = True
