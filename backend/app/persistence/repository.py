from typing import Dict, Any
from sqlmodel import Session
from .database import engine
from app.models.schemas import InterviewSession, Application
from sqlmodel import select

def save_session(session_data: Dict[str, Any]) -> None:
    """
    Save interview session metadata to database.
    """
    with Session(engine) as session:
        # Find application
        app_id = session_data.get("application_id")
        
        if not app_id:
            # Fallback: If candidate_id is numeric, it's a seeker_id. 
            try:
                cid = int(session_data["candidate_id"])
                stmt = select(Application).where(Application.seeker_id == cid).order_by(Application.created_at.desc())
                app = session.exec(stmt).first()
                if app:
                    app_id = app.id
            except:
                pass

        # Create the InterviewSession record
        new_session = InterviewSession(
            session_id=str(session_data["session_id"]),
            application_id=app_id or 1, # Default to 1 for demo if not linked
            started_at=session_data["started_at"],
            ended_at=session_data["ended_at"],
            video_path=str(session_data["video_path"]),
            audio_path=str(session_data["audio_path"]),
            multiple_faces_detected=session_data["multiple_faces_detected"],
            audio_interruptions_detected=session_data["audio_interruptions_detected"]
        )
        
        session.add(new_session)
        session.commit()
