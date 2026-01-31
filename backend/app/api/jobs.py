from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional

from app.persistence.database import get_db
from app.models.schemas import Job, User, UserRole
from app.api.auth import get_current_user, get_recruiter_user

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/", response_model=Job)
async def create_job(
    job_data: Job, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Create a new job posting. Only for recruiters/admins."""
    if current_user.role != UserRole.ADMIN:
        job_data.recruiter_id = current_user.id
        
    db.add(job_data)
    db.commit()
    db.refresh(job_data)
    return job_data

@router.get("/", response_model=List[Job])
async def list_jobs(db: Session = Depends(get_db)):
    """List all active jobs."""
    statement = select(Job).where(Job.is_active == True)
    results = db.exec(statement).all()
    return results

@router.get("/recruiter/{recruiter_id}", response_model=List[Job])
async def list_recruiter_jobs(
    recruiter_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List jobs posted by a specific recruiter. Only for recruiter themselves or admin."""
    if current_user.role == UserRole.SEEKER:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    if current_user.role == UserRole.RECRUITER and current_user.id != recruiter_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

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
