from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
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

class ApplicationWithSeeker(BaseModel):
    """Application enriched with seeker details for the recruiter console."""
    id: int
    seeker_id: int
    job_id: int
    status: str
    resume_path: Optional[str]
    created_at: datetime
    seeker_name: str
    seeker_email: str

    class Config:
        from_attributes = True


@router.get("/job/{job_id}", response_model=List[ApplicationWithSeeker])
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

    statement = select(Application, User).join(User, Application.seeker_id == User.id).where(Application.job_id == job_id)
    results = db.exec(statement).all()
    
    return [
        ApplicationWithSeeker(
            id=app.id,
            seeker_id=app.seeker_id,
            job_id=app.job_id,
            status=app.status,
            resume_path=app.resume_path,
            created_at=app.created_at,
            seeker_name=user.full_name,
            seeker_email=user.email,
        )
        for app, user in results
    ]

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

@router.post("/{application_id}/finish", response_model=Application)
async def finish_interview(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an interview as finished. Called by the seeker upon completion."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Security: Verify ownership
    if current_user.role == UserRole.SEEKER and application.seeker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    application.status = "Interviewed"
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

@router.get("/{application_id}/resume")
async def get_application_resume(
    application_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Retrieve the resume file for an application. Only for recruiters/admins."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Security: Verify ownership or admin role
    job = db.get(Job, application.job_id)
    if current_user.role != UserRole.ADMIN and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this resume")
    
    if not application.resume_path or not os.path.exists(application.resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    return FileResponse(application.resume_path)


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

class ApplicationWithJob(BaseModel):
    """Application enriched with job details for the dashboard."""
    id: int
    seeker_id: int
    job_id: int
    status: str
    resume_path: Optional[str]
    created_at: datetime
    job_title: str
    job_location: Optional[str]

    class Config:
        from_attributes = True


@router.get("/me", response_model=List[ApplicationWithJob])
async def list_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List applications for the currently logged-in seeker, enriched with job details."""
    statement = select(Application, Job).join(Job, Application.job_id == Job.id).where(
        Application.seeker_id == current_user.id
    )
    results = db.exec(statement).all()

    return [
        ApplicationWithJob(
            id=app.id,
            seeker_id=app.seeker_id,
            job_id=app.job_id,
            status=app.status,
            resume_path=app.resume_path,
            created_at=app.created_at,
            job_title=job.title,
            job_location=job.location,
        )
        for app, job in results
    ]
@router.get("/recruiter/all", response_model=List[ApplicationWithJob])
async def list_recruiter_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """List all applications for all jobs managed by the current recruiter."""
    # If admin, they might want all apps or just theirs? 
    # Usually recruiters want theirs. Admin can see everything if we don't filter.
    if current_user.role == UserRole.ADMIN:
        statement = select(Application, Job).join(Job, Application.job_id == Job.id)
    else:
        statement = select(Application, Job).join(Job, Application.job_id == Job.id).where(
            Job.recruiter_id == current_user.id
        )
        
    results = db.exec(statement).all()

    return [
        ApplicationWithJob(
            id=app.id,
            seeker_id=app.seeker_id,
            job_id=app.job_id,
            status=app.status,
            resume_path=app.resume_path,
            created_at=app.created_at,
            job_title=job.title,
            job_location=job.location,
        )
        for app, job in results
    ]
