from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
from pathlib import Path

from app.persistence.database import get_db
from app.models.schemas import Application, Job, User, UserRole, InterviewSession
from app.api.auth import get_current_user, get_admin_user, get_recruiter_user

router = APIRouter(prefix="/api/applications", tags=["applications"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class StatusUpdateRequest(BaseModel):
    status: str

@router.get("/job/{job_id}", response_model=List[Application])
async def list_job_applications(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """List all applications for a specific job. Only for recruiters/admins."""
    # Security: Verify if recruiter owns the job (if not admin)
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if current_user.role != UserRole.ADMIN and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view applications for this job")

    statement = select(Application).where(Application.job_id == job_id)
    results = db.exec(statement).all()
    return results

@router.patch("/{application_id}/status", response_model=Application)
async def update_application_status(
    application_id: int, 
    request: StatusUpdateRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Update the status of an application. Only for recruiters/admins."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Security Check
    job = db.get(Job, application.job_id)
    if current_user.role != UserRole.ADMIN and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    application.status = request.status
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/{application_id}/sessions", response_model=List[InterviewSession])
async def get_application_sessions(
    application_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interview sessions associated with an application. Authorized users only."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Security Check: Own account OR Recruiter/Admin
    if current_user.role == UserRole.SEEKER and application.seeker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Recruiter check
    if current_user.role == UserRole.RECRUITER:
        job = db.get(Job, application.job_id)
        if job.recruiter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    statement = select(InterviewSession).where(InterviewSession.application_id == application_id)
    results = db.exec(statement).all()
    return results

@router.post("/apply", response_model=Application)
async def apply_to_job(
    job_id: int = Form(...),
    seeker_id: int = Form(...),
    resume: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply for a specific job with resume upload. Only seekers can apply."""
    # Security Check
    if current_user.role == UserRole.SEEKER and current_user.id != seeker_id:
        raise HTTPException(status_code=403, detail="Cannot apply as another user")
    # 1. Verify Job exists
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # 2. Verify User exists and is a seeker or admin
    seeker = db.get(User, seeker_id)
    if not seeker or (seeker.role != UserRole.SEEKER and seeker.role != UserRole.ADMIN):
        raise HTTPException(status_code=400, detail="Only seekers can apply for jobs")
    
    # 3. Check for existing application
    statement = select(Application).where(
        Application.job_id == job_id,
        Application.seeker_id == seeker_id
    )
    existing = db.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Application already submitted for this job")
    
    # 4. Handle File Upload
    resume_path = None
    if resume:
        file_ext = os.path.splitext(resume.filename)[1]
        file_name = f"resume_{seeker_id}_{job_id}{file_ext}"
        file_path = UPLOAD_DIR / file_name
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        resume_path = str(file_path)
    
    # 5. Resume Screening (if resume provided)
    initial_status = "Applied"
    screening_result = None
    
    if resume_path:
        try:
            from app.utils.resume_parser import screen_resume
            # Determine domain from job title
            job_title_lower = job.title.lower()
            if "ai" in job_title_lower or "ml" in job_title_lower or "machine" in job_title_lower or "data" in job_title_lower:
                domain = "AI-ML"
            elif "security" in job_title_lower or "cyber" in job_title_lower:
                domain = "Cybersecurity"
            else:
                domain = "Fullstack"
            
            screening_result = screen_resume(resume_path, domain)
            
            if screening_result.get("eligible"):
                initial_status = "Interview Required"
            else:
                initial_status = "Under Review"
        except Exception as e:
            print(f"Resume screening error: {e}")
            initial_status = "Under Review"
    
    # 6. Create application
    application = Application(
        job_id=job_id,
        seeker_id=seeker_id,
        resume_path=resume_path,
        status=initial_status
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application

@router.get("/me", response_model=List[Application])
async def list_my_applications(
    seeker_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List applications for the current seeker."""
    if current_user.role == UserRole.SEEKER and current_user.id != seeker_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
        
    statement = select(Application).where(Application.seeker_id == seeker_id)
    results = db.exec(statement).all()
    return results
