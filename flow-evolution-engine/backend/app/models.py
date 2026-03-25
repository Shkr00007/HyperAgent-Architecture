from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from .db import Base


class Flow(Base):
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_text = Column(Text, nullable=False)
    flow_json = Column(Text, nullable=False)
    version_group = Column(String(50), nullable=False, index=True)
    variant_id = Column(String(20), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("flows.id"), nullable=True)
    mutation_type = Column(String(100), nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False, index=True)
    scenario = Column(Text, nullable=False)
    trace_json = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationLog(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False, index=True)
    execution_id = Column(Integer, ForeignKey("execution_logs.id"), nullable=False)
    score = Column(Float, nullable=False)
    signals_json = Column(Text, nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvolutionHistory(Base):
    __tablename__ = "evolution_history"

    id = Column(Integer, primary_key=True, index=True)
    parent_flow = Column(Integer, ForeignKey("flows.id"), nullable=False)
    child_flow = Column(Integer, ForeignKey("flows.id"), nullable=False)
    mutation_type = Column(String(100), nullable=False)
    performance_delta = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MetaLearning(Base):
    __tablename__ = "meta_learning"

    id = Column(Integer, primary_key=True, index=True)
    mutation_type = Column(String(100), nullable=False, unique=True, index=True)
    avg_score = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    wins = Column(Integer, default=0)
    trials = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
