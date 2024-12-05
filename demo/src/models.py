# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum
from datetime import datetime

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"
    WARNING = "warning"

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    branch = Column(String)
    commit = Column(String)
    author = Column(String)
    status = Column(Enum(StatusEnum))
    start_time = Column(DateTime, default=datetime.utcnow)
    duration = Column(String)
    jobs = relationship("Job", back_populates="workflow", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String)
    status = Column(Enum(StatusEnum))
    duration = Column(String)
    error = Column(String, nullable=True)
    workflow = relationship("Workflow", back_populates="jobs")
