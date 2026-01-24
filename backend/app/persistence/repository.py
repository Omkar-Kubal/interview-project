"""
Repository Module - Handles data persistence for interview sessions.
"""
from typing import Dict, Any
from .database import get_connection

def save_session(session_data: Dict[str, Any]) -> None:
    """
    Save interview session metadata to database.
    
    Args:
        session_data: Dictionary containing session details
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO interview_sessions (
            session_id,
            candidate_id,
            role,
            started_at,
            ended_at,
            video_path,
            audio_path,
            multiple_faces_detected,
            audio_interruptions_detected
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(session_data["session_id"]),
            session_data["candidate_id"],
            session_data.get("role"),
            session_data["started_at"],
            session_data["ended_at"],
            str(session_data["video_path"]),
            str(session_data["audio_path"]),
            session_data["multiple_faces_detected"],
            session_data["audio_interruptions_detected"]
        ))
        
        conn.commit()
    finally:
        conn.close()
