from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel

from app.persistence.database import get_db
from app.models.schemas import Application, Job, User, UserRole, InterviewSession

router = APIRouter(prefix="/api/applications", tags=["applications"])

class StatusUpdateRequest(BaseModel):
    status: str

@router.get("/job/{job_id}", response_model=List[Application])
async def list_job_applications(job_id: int, db: Session = Depends(get_db)):
    """List all applications for a specific job."""
    statement = select(Application).where(Application.job_id == job_id)
    results = db.exec(statement).all()
    return results

@router.patch("/{application_id}/status", response_model=Application)
async def update_application_status(
    application_id: int, 
    request: StatusUpdateRequest, 
    db: Session = Depends(get_db)
):
    """Update the status of an application."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.status = request.status
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/{application_id}/sessions", response_model=List[InterviewSession])
async def get_application_sessions(application_id: int, db: Session = Depends(get_db)):
    """Get interview sessions associated with an application."""
    statement = select(InterviewSession).where(InterviewSession.application_id == application_id)
    results = db.exec(statement).all()
    return results

class ApplyRequest(BaseModel):
    job_id: int
    seeker_id: int # In a real app, this would come from JWT 'sub'
    resume_path: Optional[str] = None

@router.post("/apply", response_model=Application)
async def apply_to_job(request: ApplyRequest, db: Session = Depends(get_db)):
    """Apply for a specific job."""
    # 1. Verify Job exists
    job = db.get(Job, request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # 2. Verify User exists and is a seeker
    seeker = db.get(User, request.seeker_id)
    if not seeker or seeker.role != UserRole.SEEKER:
        raise HTTPException(status_code=400, detail="Only seekers can apply for jobs")
    
    # 3. Check for existing application
    statement = select(Application).where(
        Application.job_id == request.job_id,
        Application.seeker_id == request.seeker_id
    )
    existing = db.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already submitted for this job")
    
    # 4. Create application
    application = Application(
        job_id=request.job_id,
        seeker_id=request.seeker_id,
        resume_path=request.resume_path,
        status="Applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/me", response_model=List[Application])
async def list_my_applications(seeker_id: int, db: Session = Depends(get_db)):
    """List applications for the current seeker."""
    # In production, seeker_id comes from auth token
    statement = select(Application).where(Application.seeker_id == seeker_id)
    results = db.exec(statement).all()
    return results
