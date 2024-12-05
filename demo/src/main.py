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