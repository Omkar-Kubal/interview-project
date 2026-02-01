"""
FastAPI Server - Main entry point for Signal Capture API.
"""
import os
import time
from datetime import datetime
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import cv2

from app.persistence.database import get_db, init_db
from app.models.schemas import User, UserRole, Application
from app.api.auth import get_current_user, get_admin_user, get_recruiter_user
from app.api.session import (
    get_session, 
    create_session, 
    clear_session, 
    StartRequest, 
    StartResponse, 
    StopResponse
)
from app.api import auth, jobs, applications, questions


# Create FastAPI app
app = FastAPI(
    title="AI Interview - Signal Capture API",
    description="Backend API for multimodal candidate signal capture",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files - look for frontend in sibling directory
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Mount storage for candidate media/answers (videos, audio, JSON)
storage_path = Path(__file__).parent.parent / "storage"
if not storage_path.exists():
    storage_path.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")

# Mount legacy data for interview replay (keeps compatibility)
data_path = Path(__file__).parent.parent / "data"
if data_path.exists():
    app.mount("/data", StaticFiles(directory=str(data_path)), name="data")

# Mount uploads for resumes
uploads_path = Path(__file__).parent.parent / "uploads"
if not uploads_path.exists():
    uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(questions.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend."""
    index_path = frontend_path / "pages" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>AI Interview - Signal Capture API</h1><p>Frontend not found.</p>")


@app.get("/capture", response_class=HTMLResponse)
async def capture_page():
    """Serve capture page."""
    capture_path = frontend_path / "pages" / "capture.html"
    if capture_path.exists():
        return FileResponse(str(capture_path))
    return HTMLResponse("<h1>Capture page not found</h1>")


@app.get("/summary", response_class=HTMLResponse)
async def summary_page():
    """Serve summary page."""
    summary_path = frontend_path / "pages" / "summary.html"
    if summary_path.exists():
        return FileResponse(str(summary_path))
    return HTMLResponse("<h1>Summary page not found</h1>")


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve login page."""
    login_path = frontend_path / "pages" / "login.html"
    if login_path.exists():
        return FileResponse(str(login_path))
    return HTMLResponse("<h1>Login page not found</h1>")


@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Serve registration page."""
    register_path = frontend_path / "pages" / "register.html"
    if register_path.exists():
        return FileResponse(str(register_path))
    return HTMLResponse("<h1>Registration page not found</h1>")


@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page():
    """Serve job board page."""
    jobs_path = frontend_path / "pages" / "jobs.html"
    if jobs_path.exists():
        return FileResponse(str(jobs_path))
    return HTMLResponse("<h1>Job board page not found</h1>")


@app.get("/apply", response_class=HTMLResponse)
async def apply_page():
    """Serve job application page."""
    apply_path = frontend_path / "pages" / "apply.html"
    if apply_path.exists():
        return FileResponse(str(apply_path))
    return HTMLResponse("<h1>Application page not found</h1>")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """Serve candidate dashboard page."""
    dashboard_path = frontend_path / "pages" / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path))
    return HTMLResponse("<h1>Dashboard page not found</h1>")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """Serve recruiter admin page."""
    admin_path = frontend_path / "pages" / "admin.html"
    if admin_path.exists():
        return FileResponse(str(admin_path))
    return HTMLResponse("<h1>Admin page not found</h1>")


@app.get("/replay", response_class=HTMLResponse)
async def replay_page():
    """Serve session replay page."""
    replay_path = frontend_path / "pages" / "replay.html"
    if replay_path.exists():
        return FileResponse(str(replay_path))
    return HTMLResponse("<h1>Replay page not found</h1>")


@app.get("/interview", response_class=HTMLResponse)
async def interview_page():
    """Serve interview questionnaire page."""
    interview_path = frontend_path / "pages" / "interview.html"
    if interview_path.exists():
        return FileResponse(str(interview_path))
    return HTMLResponse("<h1>Interview page not found</h1>")


@app.get("/review", response_class=HTMLResponse)
async def review_answers_page():
    """Serve recruiter answer review page."""
    review_path = frontend_path / "pages" / "review_answers.html"
    if review_path.exists():
        return FileResponse(str(review_path))
    return HTMLResponse("<h1>Review page not found</h1>")


@app.get("/summary", response_class=HTMLResponse)
async def summary_page():
    """Serve session summary page."""
    summary_path = frontend_path / "pages" / "summary.html"
    if summary_path.exists():
        return FileResponse(str(summary_path))
    return HTMLResponse("<h1>Summary page not found</h1>")


@app.post("/api/session/start", response_model=StartResponse)
async def start_session(request: StartRequest, current_user: User = Depends(get_current_user)):
    """Start a new capture session."""
    # Security: Seekers can only start their own sessions
    if current_user.role == UserRole.SEEKER and str(current_user.id) != request.candidate_id:
        raise HTTPException(status_code=403, detail="Not authorized to start session for another candidate")
    
    # Check if session already running for this candidate
    existing = get_session(candidate_id=request.candidate_id)
    if existing and existing.is_running:
        raise HTTPException(status_code=400, detail="Session already running for this candidate")
    
    # Create and setup session
    session = create_session(request.candidate_id)
    
    # Start capture
    try:
        session_dir = session.setup(request.candidate_id, application_id=request.application_id)
        if not session.start():
            clear_session(request.candidate_id)
            raise HTTPException(status_code=500, detail="Failed to start capture: Camera or Microphone may be unavailable")
    except Exception as e:
        clear_session(request.candidate_id)
        raise HTTPException(status_code=500, detail=f"Capture error: {str(e)}")
    
    return StartResponse(
        status="started",
        candidate_id=request.candidate_id,
        session_dir=session_dir
    )


@app.post("/api/session/stop", response_model=StopResponse)
async def stop_session(candidate_id: str, current_user: User = Depends(get_current_user)):
    """Stop the current capture session for a candidate."""
    # Security Check
    if current_user.role == UserRole.SEEKER and str(current_user.id) != candidate_id:
        raise HTTPException(status_code=403, detail="Not authorized to stop session for another candidate")
        
    session = get_session(candidate_id=candidate_id)
    if not session:
        raise HTTPException(status_code=400, detail="No active session for this candidate")
    
    # Stop capture
    try:
        result = session.stop()
        clear_session(candidate_id)
    except Exception as e:
        print(f"Error during session stop: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")
    
    return StopResponse(
        status="stopped",
        candidate_id=result["candidate_id"],
        duration_sec=result["duration_sec"]
    )


@app.post("/api/session/heartbeat")
async def session_heartbeat(candidate_id: str, current_user: User = Depends(get_current_user)):
    """Update heartbeat for a session to prevent auto-cleanup."""
    # Security Check
    if current_user.role == UserRole.SEEKER and str(current_user.id) != candidate_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session = get_session(candidate_id=candidate_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.update_heartbeat()
    return {"status": "ok", "timestamp": time.time()}


async def session_cleanup_task():
    """Background task to clean up orphaned sessions (1 minute timeout)."""
    while True:
        try:
            from app.api.session import _active_sessions, clear_session
            
            current_time = time.time()
            to_delete = []
            
            # Check all active sessions
            for cid, session in list(_active_sessions.items()):
                # If no heartbeat for > 60 seconds, it's orphaned
                if current_time - session.last_heartbeat > 60:
                    print(f"[CLEANUP] Session for {cid} timed out (1 min). Stopping...")
                    to_delete.append(cid)
            
            for cid in to_delete:
                session = _active_sessions[cid]
                try:
                    session.stop()
                except Exception as e:
                    print(f"[CLEANUP] Error stopping session {cid}: {e}")
                clear_session(cid)
                
        except Exception as e:
            print(f"[CLEANUP] error in background task: {e}")
            
        await asyncio.sleep(10) # Check every 10 seconds


@app.on_event("startup")
async def on_startup():
    """Startup tasks."""
    # Initialize database
    init_db()
    print("[SERVER] Database initialized.")
    # Start the background cleanup task
    asyncio.create_task(session_cleanup_task())
    print("Background session cleanup task started (1 min timeout).")


@app.get("/api/session/summary")
async def get_summary(candidate_id: str, current_user: User = Depends(get_current_user)):
    """Get session summary."""
    # Security: Seekers check own ID, Recruiters/Admins allowed
    if current_user.role == UserRole.SEEKER and str(current_user.id) != candidate_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    session = get_session(candidate_id=candidate_id)
    if not session:
        # Check if we can find a finished session in history (optional extension)
        raise HTTPException(status_code=400, detail="No active session found")
    
    return session.get_summary()


@app.websocket("/api/session/live")
async def websocket_live(websocket: WebSocket, candidate_id: Optional[str] = None):
    """WebSocket endpoint for live signal stream."""
    await websocket.accept()
    
    try:
        while True:
            session = get_session(candidate_id=candidate_id)
            
            if session and session.is_running:
                signals = session.get_current_signals()
                await websocket.send_json(signals)
            else:
                # Send idle state
                await websocket.send_json({
                    "face_detected": False,
                    "eye_direction": "unknown",
                    "head_movement": "unknown",
                    "blink": False,
                    "voice_activity": "silent",
                    "integrity": {
                        "face_continuous": False,
                        "multiple_faces": False,
                        "audio_interruptions": False
                    },
                    "elapsed_sec": 0,
                    "session_active": False
                })
            
            # 200ms interval
            await asyncio.sleep(0.2)
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    session = get_session()
    return {
        "status": "healthy",
        "session_active": session.is_running if session else False
    }


async def generate_frames(candidate_id: Optional[str] = None):
    """Generate MJPEG frames from current session (async for non-blocking)."""
    print(f"[MJPEG] Starting async frame generator for {candidate_id or 'default'}...")
    frame_counter = 0
    
    while True:
        session = get_session(candidate_id=candidate_id)
        if session and session.is_running:
            frame = session.get_current_frame()
            if frame is not None:
                # Encode frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    frame_counter += 1
                    if frame_counter % 30 == 0:
                        print(f"[MJPEG] Streamed {frame_counter} frames")
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # No frame available yet, wait briefly
                await asyncio.sleep(0.05)
        else:
            # No active session - wait briefly
            await asyncio.sleep(0.1)
        
        # Small sleep to prevent CPU overload and yield control
        await asyncio.sleep(0.033)  # ~30 FPS max


@app.get("/video_feed")
async def video_feed(candidate_id: Optional[str] = None):
    """MJPEG video stream endpoint."""
    return StreamingResponse(
        generate_frames(candidate_id=candidate_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )



# Run with: uvicorn app.main:app --reload
