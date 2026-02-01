from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class UserRole(str, Enum):
    RECRUITER = "recruiter"
    SEEKER = "seeker"
    ADMIN = "admin"

class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    full_name: str
    role: UserRole = UserRole.SEEKER

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    jobs: List["Job"] = Relationship(back_populates="recruiter")
    applications: List["Application"] = Relationship(back_populates="seeker")

class JobBase(SQLModel):
    title: str
    description: str
    location: str
    salary_range: Optional[str] = None
    is_active: bool = True

class Job(JobBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recruiter_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    recruiter: User = Relationship(back_populates="jobs")
    applications: List["Application"] = Relationship(back_populates="job")

class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seeker_id: int = Field(foreign_key="user.id")
    job_id: int = Field(foreign_key="job.id")
    status: str = Field(default="Applied") # Applied, Interviewed, Offered, Rejected
    resume_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    seeker: User = Relationship(back_populates="applications")
    job: Job = Relationship(back_populates="applications")
    interview_session: Optional["InterviewSession"] = Relationship(back_populates="application")

class InterviewSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    session_id: str = Field(index=True, unique=True) # The UUID used in file paths
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    multiple_faces_detected: bool = False
    audio_interruptions_detected: bool = False
    
    # Relationships
    application: Application = Relationship(back_populates="interview_session")


# ============ QUESTIONNAIRE MODELS ============

class QuestionType(str, Enum):
    MCQ = "mcq"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class Question(SQLModel, table=True):
    """Individual interview question."""
    id: Optional[int] = Field(default=None, primary_key=True)
    domain: str  # e.g., "AI-ML", "Fullstack", "Cybersecurity"
    question_text: str
    question_type: QuestionType
    options: Optional[str] = None  # JSON string for MCQ options
    correct_option: Optional[int] = None  # Index (0-based) for MCQ correct answer
    time_limit_sec: int = 120  # Default 2 minutes
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Questionnaire(SQLModel, table=True):
    """Links a set of questions to a job posting."""
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    name: str = "Default Questionnaire"
    question_ids: str  # Comma-separated question IDs (e.g., "1,2,3,4,5")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CandidateAnswer(SQLModel, table=True):
    """Stores a candidate's answer to a single question."""
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    question_id: int = Field(foreign_key="question.id")
    answer_type: QuestionType
    answer_text: Optional[str] = None  # For MCQ choice or text answer
    answer_file_path: Optional[str] = None  # For video/audio file
    score: Optional[float] = None  # Recruiter or auto-score (0-100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
