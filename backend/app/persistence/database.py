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
    from app.models.schemas import User, Job, Application, InterviewSession, UserRole, Question, Questionnaire, QuestionType
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
            # 3. Create Default Questions
            q1 = Question(
                domain="General",
                question_text="Tell us about yourself and your background.",
                question_type=QuestionType.VIDEO,
                time_limit_sec=120
            )
            q2 = Question(
                domain="General",
                question_text="Why are you interested in this role?",
                question_type=QuestionType.AUDIO,
                time_limit_sec=60
            )
            q3 = Question(
                domain="General",
                question_text="What is your greatest technical strength?",
                question_type=QuestionType.TEXT,
                time_limit_sec=180
            )
            q4 = Question(
                domain="General",
                question_text="Which keyword is used to define a function in Python?",
                question_type=QuestionType.MCQ,
                options='["func", "define", "def", "function"]',
                correct_option=2,
                time_limit_sec=30
            )
            session.add_all([q1, q2, q3, q4])
            session.commit()
            session.refresh(q1); session.refresh(q2); session.refresh(q3); session.refresh(q4)

            # 4. Create Questionnaire for the sample job
            questionnaire = Questionnaire(
                job_id=job.id,
                name="Standard Assessment",
                question_ids=f"{q1.id},{q2.id},{q3.id},{q4.id}"
            )
            session.add(questionnaire)
            session.commit()
            
            print(f"[DB] Seed complete. Admin: admin@example.com / admin123")
        else:
            # Enhancement: Check if any existing jobs are missing questionnaires
            jobs = session.exec(select(Job)).all()
            for j in jobs:
                stmt = select(Questionnaire).where(Questionnaire.job_id == j.id)
                if not session.exec(stmt).first():
                    # Create default questionnaire for existing job
                    questions = session.exec(select(Question)).all()
                    if questions:
                        q_ids = ",".join([str(q.id) for q in questions[:4]])
                        qn = Questionnaire(job_id=j.id, question_ids=q_ids)
                        session.add(qn)
            session.commit()

def get_db():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session
