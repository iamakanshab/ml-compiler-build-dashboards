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

# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./pytorch_hud.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .models import StatusEnum

class JobBase(BaseModel):
    name: str
    status: StatusEnum
    duration: str
    error: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    workflow_id: int

    class Config:
        orm_mode = True

class WorkflowBase(BaseModel):
    name: str
    branch: str
    commit: str
    author: str
    status: StatusEnum
    duration: str

class WorkflowCreate(WorkflowBase):
    pass

class Workflow(WorkflowBase):
    id: int
    start_time: datetime
    jobs: List[Job]

    class Config:
        orm_mode = True

# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db, init_db
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="PyTorch HUD API")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/workflows/", response_model=List[schemas.Workflow])
def get_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workflows = db.query(models.Workflow).offset(skip).limit(limit).all()
    return workflows

@app.get("/workflows/{workflow_id}", response_model=schemas.Workflow)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@app.post("/workflows/", response_model=schemas.Workflow)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = models.Workflow(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@app.post("/workflows/{workflow_id}/jobs/", response_model=schemas.Job)
def create_job(workflow_id: int, job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.dict(), workflow_id=workflow_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.put("/workflows/{workflow_id}/status", response_model=schemas.Workflow)
def update_workflow_status(workflow_id: int, status: StatusEnum, db: Session = Depends(get_db)):
    workflow = db.query(models.Workflow).filter(models.Workflow.id == workflow_id).first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow.status = status
    db.commit()
    db.refresh(workflow)
    return workflow

# app/utils.py
def calculate_duration(start_time: datetime) -> str:
    duration = datetime.utcnow() - start_time
    minutes = duration.total_seconds() / 60
    return f"{int(minutes)}m"

# app/github_client.py
from typing import Optional
import aiohttp
import asyncio

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}" if token else None
        }

    async def get_workflow_runs(self, owner: str, repo: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"
            async with session.get(url, headers=self.headers) as response:
                return await response.json()

    async def get_workflow_jobs(self, owner: str, repo: str, run_id: int):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
            async with session.get(url, headers=self.headers) as response:
                return await response.json()

# app/poller.py
import asyncio
from datetime import datetime
from .database import SessionLocal
from .github_client import GitHubClient
from .models import Workflow, Job, StatusEnum

class WorkflowPoller:
    def __init__(self, github_token: str, poll_interval: int = 60):
        self.github_client = GitHubClient(github_token)
        self.poll_interval = poll_interval

    async def poll_workflows(self):
        while True:
            try:
                workflows = await self.github_client.get_workflow_runs("pytorch", "pytorch")
                self._update_database(workflows)
            except Exception as e:
                print(f"Error polling workflows: {e}")
            await asyncio.sleep(self.poll_interval)

    def _update_database(self, workflows):
        db = SessionLocal()
        try:
            for workflow_data in workflows["workflow_runs"]:
                workflow = db.query(Workflow).filter_by(id=workflow_data["id"]).first()
                if not workflow:
                    workflow = Workflow(
                        id=workflow_data["id"],
                        name=workflow_data["name"],
                        branch=workflow_data["head_branch"],
                        commit=workflow_data["head_sha"],
                        author=workflow_data["actor"]["login"],
                        status=self._map_github_status(workflow_data["status"]),
                        start_time=datetime.fromisoformat(workflow_data["created_at"].replace("Z", "+00:00")),
                        duration=self._calculate_duration(workflow_data["created_at"])
                    )
                    db.add(workflow)
                db.commit()
        finally:
            db.close()

    def _map_github_status(self, status: str) -> StatusEnum:
        status_mapping = {
            "completed": StatusEnum.SUCCESS,
            "in_progress": StatusEnum.RUNNING,
            "queued": StatusEnum.PENDING,
            "failed": StatusEnum.FAILED
        }
        return status_mapping.get(status, StatusEnum.WARNING)

    def _calculate_duration(self, start_time: str) -> str:
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        duration = datetime.utcnow() - start
        return f"{int(duration.total_seconds() / 60)}m"

# requirements.txt
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.23
pydantic>=1.8.2
aiohttp>=3.8.1
python-dotenv>=0.19.0
