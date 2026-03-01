from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
import time

from app.persistence.database import get_db
from app.models.schemas import Job, User, UserRole, Question, Questionnaire, JobCreate
from app.api.auth import get_current_user, get_recruiter_user

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# Enhancement #5: Simple in-memory cache for job listings
_jobs_cache = {"data": None, "timestamp": 0}
CACHE_TTL_SECONDS = 60  # Cache for 60 seconds

@router.post("/", response_model=Job)
async def create_job(
    request: JobCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Create a new job posting with an optional custom questionnaire."""
    # Create the job object
    job = Job(
        title=request.title,
        description=request.description,
        location=request.location,
        category=request.category,
        salary_range=request.salary_range,
        recruiter_id=current_user.id if current_user.role != UserRole.ADMIN else 1 # Default admin
    )
    
    # Invalidate cache
    _jobs_cache["data"] = None
    _jobs_cache["timestamp"] = 0
        
    db.add(job)
    db.commit()
    db.refresh(job)

    # Process custom questions if provided
    import json
    q_ids = []
    
    if request.questions and len(request.questions) > 0:
        for q_data in request.questions:
            new_q = Question(
                domain=q_data.domain or job.category or "General",
                question_text=q_data.question_text,
                question_type=q_data.question_type,
                options=json.dumps(q_data.options) if q_data.options else None,
                correct_option=q_data.correct_option,
                time_limit_sec=q_data.time_limit_sec
            )
            db.add(new_q)
            db.commit()
            db.refresh(new_q)
            q_ids.append(str(new_q.id))
    else:
        # Fallback to default questions if none provided
        default_qs = db.exec(select(Question)).all()
        if default_qs:
            q_ids = [str(q.id) for q in default_qs[:4]]

    if q_ids:
        questionnaire = Questionnaire(
            job_id=job.id,
            name=f"Assessment for {job.title}",
            question_ids=",".join(q_ids)
        )
        db.add(questionnaire)
        db.commit()

    return job

@router.get("/", response_model=List[Job])
async def list_jobs(db: Session = Depends(get_db)):
    """List all active jobs with caching."""
    global _jobs_cache
    
    # Check cache validity
    if _jobs_cache["data"] is not None and (time.time() - _jobs_cache["timestamp"]) < CACHE_TTL_SECONDS:
        return _jobs_cache["data"]
    
    # Fetch from database
    statement = select(Job).where(Job.is_active == True)
    results = db.exec(statement).all()
    
    # Update cache
    _jobs_cache["data"] = list(results)
    _jobs_cache["timestamp"] = time.time()
    
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

@router.patch("/{job_id}/status", response_model=Job)
async def update_job_status(
    job_id: int, 
    status_data: dict, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Toggle job status (Active/Closed)."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Security check: Only owner or admin
    if current_user.role != UserRole.ADMIN and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to modify this job")
    
    job.is_active = status_data.get("is_active", job.is_active)
    
    # Invalidate cache
    _jobs_cache["data"] = None
    _jobs_cache["timestamp"] = 0
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.patch("/{job_id}", response_model=Job)
async def patch_job(
    job_id: int, 
    request: JobCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Update job details and questionnaire."""
    db_job = db.get(Job, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Security check: Only owner or admin
    if current_user.role != UserRole.ADMIN and db_job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to modify this job")
    
    # Update job fields
    db_job.title = request.title or db_job.title
    db_job.description = request.description or db_job.description
    db_job.location = request.location or db_job.location
    db_job.category = request.category or db_job.category
    db_job.salary_range = request.salary_range or db_job.salary_range
    
    # Invalidate cache
    _jobs_cache["data"] = None
    _jobs_cache["timestamp"] = 0
    
    db.add(db_job)
    db.commit()

    # Handle Question Updates if provided
    if request.questions is not None:
        import json
        q_ids = []
        for q_data in request.questions:
            new_q = Question(
                domain=q_data.domain or db_job.category or "General",
                question_text=q_data.question_text,
                question_type=q_data.question_type,
                options=json.dumps(q_data.options) if q_data.options else None,
                correct_option=q_data.correct_option,
                time_limit_sec=q_data.time_limit_sec
            )
            db.add(new_q)
            db.commit()
            db.refresh(new_q)
            q_ids.append(str(new_q.id))
        
        if q_ids:
            # Update or create questionnaire
            statement = select(Questionnaire).where(Questionnaire.job_id == job_id)
            existing_qn = db.exec(statement).first()
            if existing_qn:
                existing_qn.question_ids = ",".join(q_ids)
                db.add(existing_qn)
            else:
                new_qn = Questionnaire(
                    job_id=job_id,
                    name=f"Assessment for {db_job.title}",
                    question_ids=",".join(q_ids)
                )
                db.add(new_qn)
            db.commit()

    db.refresh(db_job)
    return db_job

@router.put("/{job_id}", response_model=Job)

@router.delete("/{job_id}")
async def delete_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_recruiter_user)
):
    """Delete a job posting."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Security check: Only owner or admin
    if current_user.role != UserRole.ADMIN and job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this job")
    
    # Invalidate cache
    _jobs_cache["data"] = None
    _jobs_cache["timestamp"] = 0
    
    db.delete(job)
    db.commit()
    return {"detail": "Job deleted successfully"}

