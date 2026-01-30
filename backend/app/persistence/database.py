from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path
import os

DB_FILE = "interview.db"
sqlite_url = f"sqlite:///./{DB_FILE}"

# Connect args needed for SQLite to avoid threading issues in FastAPI
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def init_db():
    """Create all tables and seed initial data if empty."""
    from app.models.schemas import User, Job, Application, InterviewSession, UserRole
    from app.core.auth import get_password_hash
    from sqlmodel import select
    
    SQLModel.metadata.create_all(engine)
    
    # Simple seed logic
    with Session(engine) as session:
        # Check if we have users
        user_count = session.exec(select(User)).first()
        if not user_count:
            print("[DB] Seeding initial data...")
            # 1. Create a Recruiter
            recruiter = User(
                email="admin@example.com",
                full_name="System Admin",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            session.add(recruiter)
            session.commit()
            session.refresh(recruiter)
            
            # 2. Create a sample Job
            job = Job(
                title="Sr. Machine Learning Engineer",
                description="We are looking for an expert in computer vision and signal processing.",
                location="Remote / San Francisco",
                salary_range="$150k - $220k",
                recruiter_id=recruiter.id
            )
            session.add(job)
            session.commit()
            print(f"[DB] Seed complete. Admin: admin@example.com / admin123")

def get_db():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
