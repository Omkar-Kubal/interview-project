"""
Database Module - Handles SQLite connection and schema initialization.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("interview.db")

def get_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        session_id UUID PRIMARY KEY,
        candidate_id TEXT NOT NULL,
        role TEXT,
        started_at TIMESTAMP NOT NULL,
        ended_at TIMESTAMP NOT NULL,

        video_path TEXT NOT NULL,
        audio_path TEXT NOT NULL,

        multiple_faces_detected BOOLEAN DEFAULT FALSE,
        audio_interruptions_detected BOOLEAN DEFAULT FALSE,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()

# Initialize on module load
init_db()
