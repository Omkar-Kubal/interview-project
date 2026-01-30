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
