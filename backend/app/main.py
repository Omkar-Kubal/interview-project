"""
FastAPI Server - Main entry point for Signal Capture API.
"""
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from app.api.session import get_session, create_session, clear_session


# Request/Response models
class StartRequest(BaseModel):
    candidate_id: str


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


@app.post("/api/session/start", response_model=StartResponse)
async def start_session(request: StartRequest):
    """Start a new capture session."""
    # Check if session already running
    existing = get_session()
    if existing and existing.is_running:
        raise HTTPException(status_code=400, detail="Session already running")
    
    # Create and setup session
    session = create_session()
    session_dir = session.setup(request.candidate_id)
    
    # Start capture
    if not session.start():
        clear_session()
        raise HTTPException(status_code=500, detail="Failed to start capture")
    
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
    
    result = session.stop()
    
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


# Run with: uvicorn app.main:app --reload
