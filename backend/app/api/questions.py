"""
Questions API Router - Manages questionnaires and candidate answers.
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
import json
import os
import shutil
from pathlib import Path

from app.persistence.database import get_db
from app.models.schemas import (
    Question, Questionnaire, CandidateAnswer, QuestionType,
    Application, User, UserRole
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/questions", tags=["questions"])

# Base storage directory - organized by candidate
STORAGE_BASE = Path("storage/candidates")
STORAGE_BASE.mkdir(parents=True, exist_ok=True)


# ============ Response Models ============

class QuestionOut(BaseModel):
    id: int
    domain: str
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    time_limit_sec: int

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    application_id: int
    question_id: int
    answer_text: Optional[str] = None  # For MCQ/text


# ============ Endpoints ============

@router.get("/domains", response_model=List[str])
async def list_domains(db: Session = Depends(get_db)):
    """Get list of available question domains."""
    statement = select(Question.domain).distinct()
    results = db.exec(statement).all()
    return results


@router.get("/domain/{domain}", response_model=List[QuestionOut])
async def get_questions_by_domain(domain: str, db: Session = Depends(get_db)):
    """Get all questions for a specific domain."""
    statement = select(Question).where(Question.domain == domain)
    questions = db.exec(statement).all()
    
    # Parse JSON options for MCQs
    result = []
    for q in questions:
        q_out = QuestionOut(
            id=q.id,
            domain=q.domain,
            question_text=q.question_text,
            question_type=q.question_type,
            options=json.loads(q.options) if q.options else None,
            time_limit_sec=q.time_limit_sec
        )
        result.append(q_out)
    
    return result


@router.get("/job/{job_id}", response_model=List[QuestionOut])
async def get_questionnaire_for_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for a job's questionnaire."""
    # Find questionnaire for job
    statement = select(Questionnaire).where(Questionnaire.job_id == job_id)
    questionnaire = db.exec(statement).first()
    
    if not questionnaire:
        raise HTTPException(status_code=404, detail="No questionnaire found for this job")
    
    # Parse question IDs
    question_ids = [int(qid.strip()) for qid in questionnaire.question_ids.split(",")]
    
    # Fetch questions
    questions = []
    for qid in question_ids:
        q = db.get(Question, qid)
        if q:
            q_out = QuestionOut(
                id=q.id,
                domain=q.domain,
                question_text=q.question_text,
                question_type=q.question_type,
                options=json.loads(q.options) if q.options else None,
                time_limit_sec=q.time_limit_sec
            )
            questions.append(q_out)
    
    return questions


@router.post("/answer/text")
async def submit_text_answer(
    answer: AnswerSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a text/MCQ answer."""
    # Verify application belongs to user
    application = db.get(Application, answer.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if current_user.role == UserRole.SEEKER and application.seeker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Get question to determine type
    question = db.get(Question, answer.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Auto-score MCQ
    score = None
    if question.question_type == QuestionType.MCQ and question.correct_option is not None:
        try:
            selected = int(answer.answer_text)
            score = 100.0 if selected == question.correct_option else 0.0
        except:
            score = 0.0
    
    # Get candidate info for folder organization
    candidate = db.get(User, application.seeker_id)
    candidate_name = candidate.full_name if candidate else f"candidate_{application.seeker_id}"
    safe_folder_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in candidate_name)
    safe_folder_name = safe_folder_name.replace(' ', '_').lower()
    
    # Create candidate answers folder
    candidate_dir = STORAGE_BASE / safe_folder_name / "answers"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    
    # Load or create answers.json for this candidate
    answers_file = candidate_dir / "answers.json"
    answers_data = {}
    if answers_file.exists():
        with open(answers_file, "r") as f:
            answers_data = json.load(f)
    
    # Add/update this answer
    answer_record = {
        "question_id": answer.question_id,
        "question_text": question.question_text,
        "question_type": question.question_type.value,
        "domain": question.domain,
        "answer": answer.answer_text,
        "score": score,
        "timestamp": str(os.popen('date /t').read().strip())
    }
    
    # If MCQ, include selected option text
    if question.question_type == QuestionType.MCQ and question.options:
        try:
            options = json.loads(question.options)
            selected_idx = int(answer.answer_text)
            answer_record["selected_option"] = options[selected_idx] if 0 <= selected_idx < len(options) else None
            answer_record["correct_option_index"] = question.correct_option
        except:
            pass
    
    answers_data[f"q{answer.question_id}"] = answer_record
    
    # Save to JSON file
    with open(answers_file, "w") as f:
        json.dump(answers_data, f, indent=2)
    
    # Check for existing answer in DB
    statement = select(CandidateAnswer).where(
        CandidateAnswer.application_id == answer.application_id,
        CandidateAnswer.question_id == answer.question_id
    )
    existing = db.exec(statement).first()
    
    if existing:
        existing.answer_text = answer.answer_text
        existing.score = score
        existing.answer_file_path = str(answers_file)
        db.add(existing)
    else:
        new_answer = CandidateAnswer(
            application_id=answer.application_id,
            question_id=answer.question_id,
            answer_type=question.question_type,
            answer_text=answer.answer_text,
            score=score,
            answer_file_path=str(answers_file)
        )
        db.add(new_answer)
    
    db.commit()
    return {"status": "saved", "score": score, "file": str(answers_file)}


@router.post("/answer/media")
async def submit_media_answer(
    application_id: int = Form(...),
    question_id: int = Form(...),
    media_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a video/audio answer."""
    # Verify application
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if current_user.role == UserRole.SEEKER and application.seeker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get candidate info for folder organization
    candidate = db.get(User, application.seeker_id)
    candidate_name = candidate.full_name if candidate else f"candidate_{application.seeker_id}"
    # Sanitize folder name (remove special chars, replace spaces with underscores)
    safe_folder_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in candidate_name)
    safe_folder_name = safe_folder_name.replace(' ', '_').lower()
    
    # Create candidate folder
    candidate_dir = STORAGE_BASE / safe_folder_name / "answers"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file with question context in filename
    ext = os.path.splitext(media_file.filename)[1] or ".webm"
    file_name = f"q{question_id}_{question.question_type.value}{ext}"
    file_path = candidate_dir / file_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(media_file.file, buffer)
    
    # Save to database
    statement = select(CandidateAnswer).where(
        CandidateAnswer.application_id == application_id,
        CandidateAnswer.question_id == question_id
    )
    existing = db.exec(statement).first()
    
    if existing:
        existing.answer_file_path = str(file_path)
        db.add(existing)
    else:
        new_answer = CandidateAnswer(
            application_id=application_id,
            question_id=question_id,
            answer_type=question.question_type,
            answer_file_path=str(file_path)
        )
        db.add(new_answer)
    
    db.commit()
    return {"status": "uploaded", "path": str(file_path), "candidate": candidate_name}


@router.get("/answers/{application_id}", response_model=List[CandidateAnswer])
async def get_application_answers(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all answers for an application (for recruiter review)."""
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Security check
    if current_user.role == UserRole.SEEKER and application.seeker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    statement = select(CandidateAnswer).where(CandidateAnswer.application_id == application_id)
    answers = db.exec(statement).all()
    return answers


@router.patch("/answers/{answer_id}/score")
async def score_answer(
    answer_id: int,
    score: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allow recruiter to score a video/audio answer."""
    if current_user.role not in [UserRole.RECRUITER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only recruiters can score answers")
    
    answer = db.get(CandidateAnswer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    answer.score = max(0, min(100, score))  # Clamp 0-100
    db.add(answer)
    db.commit()
    
    return {"status": "scored", "score": answer.score}
