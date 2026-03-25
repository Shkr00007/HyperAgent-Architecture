from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .db import Base


class Flow(Base):
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_text = Column(Text, nullable=False)
    flow_json = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    parent_flow_id = Column(Integer, ForeignKey("flows.id"), nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Flow", remote_side=[id], uselist=False)


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    scenario = Column(Text, nullable=False)
    output_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    execution_id = Column(Integer, ForeignKey("execution_logs.id"), nullable=False)
    score = Column(Float, nullable=False)
    notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvolutionLog(Base):
    __tablename__ = "evolution_logs"

    id = Column(Integer, primary_key=True, index=True)
    old_flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    new_flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False)
    reason = Column(Text, nullable=False)
    old_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
