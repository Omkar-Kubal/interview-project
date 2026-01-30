"""
FastAPI Server - Main entry point for Signal Capture API.
"""
import os
import time
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import cv2

from app.api.session import get_session, create_session, clear_session
from app.persistence.database import init_db
from app.api import auth, jobs, applications


# Request/Response models
class StartRequest(BaseModel):
    candidate_id: str
    application_id: Optional[int] = None


class StartResponse(BaseModel):
    status: str
    candidate_id: str
    session_dir: str


class StopResponse(BaseModel):
    status: str
    candidate_id: str
    duration_sec: float


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

# Mount data for media replay
data_path = Path(__file__).parent.parent.parent / "backend" / "data"
if data_path.exists():
    app.mount("/data", StaticFiles(directory=str(data_path)), name="data")

# Include Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(applications.router)

@app.on_event("startup")
def on_startup():
    """Initialize database and common resources."""
    init_db()
    print("[SERVER] Database initialized.")


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


@app.get("/summary", response_class=HTMLResponse)
async def summary_page():
    """Serve session summary page."""
    summary_path = frontend_path / "pages" / "summary.html"
    if summary_path.exists():
        return FileResponse(str(summary_path))
    return HTMLResponse("<h1>Summary page not found</h1>")


@app.post("/api/session/start", response_model=StartResponse)
async def start_session(request: StartRequest):
    """Start a new capture session."""
    # Check if session already running
    existing = get_session()
    if existing and existing.is_running:
        raise HTTPException(status_code=400, detail="Session already running")
    
    # Create and setup session
    session = create_session()
    
    # Start capture
    try:
        session_dir = session.setup(request.candidate_id, application_id=request.application_id)
        if not session.start():
            clear_session()
            raise HTTPException(status_code=500, detail="Failed to start capture: Camera or Microphone may be unavailable")
    except Exception as e:
        clear_session()
        raise HTTPException(status_code=500, detail=f"Capture error: {str(e)}")
    
    return StartResponse(
        status="started",
        candidate_id=request.candidate_id,
        session_dir=session_dir
    )


@app.post("/api/session/stop", response_model=StopResponse)
async def stop_session():
    """Stop the current capture session."""
    session = get_session()
    if not session:
        raise HTTPException(status_code=400, detail="No active session")
    
    # Stop capture
    try:
        result = session.stop()
    except Exception as e:
        print(f"Error during session stop: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")
    
    return StopResponse(
        status="stopped",
        candidate_id=result["candidate_id"],
        duration_sec=result["duration_sec"]
    )


@app.get("/api/session/summary")
async def get_summary():
    """Get session summary."""
    session = get_session()
    if not session:
        raise HTTPException(status_code=400, detail="No session available")
    
    return session.get_summary()


@app.websocket("/api/session/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket endpoint for live signal stream."""
    await websocket.accept()
    
    try:
        while True:
            session = get_session()
            
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


async def generate_frames():
    """Generate MJPEG frames from current session (async for non-blocking)."""
    print("[MJPEG] Starting async frame generator...")
    frame_counter = 0
    
    while True:
        session = get_session()
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
async def video_feed():
    """MJPEG video stream endpoint."""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )



# Run with: uvicorn app.main:app --reload
