from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from app.persistence.database import get_db
from app.models.schemas import Job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/", response_model=List[Job])
async def list_jobs(db: Session = Depends(get_db)):
    """List all active jobs."""
    statement = select(Job).where(Job.is_active == True)
    results = db.exec(statement).all()
    return results

@router.get("/recruiter/{recruiter_id}", response_model=List[Job])
async def list_recruiter_jobs(recruiter_id: int, db: Session = Depends(get_db)):
    """List jobs posted by a specific recruiter."""
    statement = select(Job).where(Job.recruiter_id == recruiter_id)
    results = db.exec(statement).all()
    return results

@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get specific job details."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
