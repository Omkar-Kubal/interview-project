# AI Interview - Signal Capture Architecture

This document describes the complete project structure and how each component fits into the overall system.

---

## Overview

The AI Interview Signal Capture system is split into two main layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Web Interface)                     │
│           Candidate Interaction & Visualization Layer           │
├─────────────────────────────────────────────────────────────────┤
│                    BACKEND (Python API)                         │
│               Signal Ingestion & Processing Layer               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
interview-project/
│
├── backend/                      # Signal Ingestion Layer
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── cli.py                # Command-line interface
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                  # HTTP & WebSocket Routes
│   │   │   ├── __init__.py
│   │   │   └── session.py        # Session management + CaptureSession class
│   │   │
│   │   ├── capture/              # Signal Acquisition Modules
│   │   │   ├── __init__.py
│   │   │   ├── camera/           # Video Signal Processing
│   │   │   │   ├── __init__.py
│   │   │   │   ├── camera_capture.py    # OpenCV video capture + recording
│   │   │   │   ├── face_logger.py       # Face detection orchestration
│   │   │   │   ├── eye_tracking.py      # Blink + gaze direction (MediaPipe)
│   │   │   │   └── head_movement.py     # Head motion intensity tracking
│   │   │   │
│   │   │   └── audio/            # Audio Signal Processing
│   │   │       ├── __init__.py
│   │   │       ├── audio_capture.py     # PyAudio recording
│   │   │       └── voice_activity.py    # VAD (energy-based detection)
│   │   │
│   │   ├── session/              # Session Lifecycle Management
│   │   │   ├── __init__.py
│   │   │   ├── session_manager.py       # Directory creation, metadata
│   │   │   └── json_writer.py           # Thread-safe JSON logging
│   │   │
│   │   └── ui/                   # CLI Overlay (optional)
│   │       ├── __init__.py
│   │       ├── overlay.py               # OpenCV overlay rendering
│   │       └── styles.py                # Color/font constants
│   │
│   ├── data/                     # Output Directory
│   │   └── user_<candidate_id>/  # Per-candidate session data
│   │       ├── video.mp4         # Recorded video
│   │       ├── audio.wav         # Recorded audio
│   │       ├── face_log.json     # Face detection events
│   │       ├── audio_log.json    # Voice activity events
│   │       └── session_meta.json # Session metadata
│   │
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Backend documentation
│
├── frontend/                     # Candidate Interaction Layer
│   ├── pages/                    # HTML Pages
│   │   ├── index.html            # Landing page (Candidate ID entry)
│   │   ├── capture.html          # Live capture (camera/mic access)
│   │   └── summary.html          # Session complete summary
│   │
│   ├── scripts/                  # JavaScript Modules
│   │   ├── session.js            # API calls (start/stop/summary)
│   │   ├── media.js              # Camera + microphone lifecycle
│   │   ├── signals.js            # WebSocket handling
│   │   └── ui.js                 # DOM utilities + formatters
│   │
│   ├── styles/                   # CSS (uses Tailwind CDN)
│   ├── public/assets/            # Static assets
│   ├── config.js                 # Configuration constants
│   └── README.md                 # Frontend documentation
│
├── archive/                      # Old files (can be deleted)
│   ├── camera/                   # Original camera modules
│   ├── audio/                    # Original audio modules
│   ├── storage/                  # Original storage modules
│   ├── api/                      # Original API modules
│   ├── ui/                       # Original UI modules
│   ├── main.py                   # Original CLI entry
│   └── stitch_demo_landing_screen/
│
├── README.md                     # Project overview
└── architecture.md               # This file
```

---

## Component Details

### Backend Components

#### `app/main.py` - FastAPI Server
The main entry point for the web API. Serves:
- Frontend pages (`/`, `/capture`, `/summary`)
- REST API endpoints (`/api/session/*`)
- WebSocket endpoint (`/api/session/live`)

#### `app/api/session.py` - Session Management
Contains the `CaptureSession` class which:
- Orchestrates camera, audio, and face logging
- Provides thread-safe signal access
- Tracks session integrity metrics

#### `app/capture/camera/` - Video Processing
| Module | Purpose |
|--------|---------|
| `camera_capture.py` | OpenCV video capture, MP4 recording, FPS tracking |
| `face_logger.py` | Orchestrates eye/head/face detection per frame |
| `eye_tracking.py` | MediaPipe Face Mesh for blink + gaze detection |
| `head_movement.py` | Landmark-based head motion intensity |

#### `app/capture/audio/` - Audio Processing
| Module | Purpose |
|--------|---------|
| `audio_capture.py` | PyAudio WAV recording with chunk callbacks |
| `voice_activity.py` | Energy-based voice activity detection (VAD) |

#### `app/session/` - Lifecycle Management
| Module | Purpose |
|--------|---------|
| `session_manager.py` | Creates directories, tracks metadata |
| `json_writer.py` | Thread-safe JSON logging for face/audio events |

---

### Frontend Components

#### Pages
| Page | Purpose | Camera Access |
|------|---------|---------------|
| `index.html` | Enter Candidate ID, start session | ❌ No |
| `capture.html` | Live video feed, signal display | ✅ Yes |
| `summary.html` | Session complete, restart option | ❌ No |

#### JavaScript Modules
| Module | Purpose |
|--------|---------|
| `session.js` | `startSession()`, `stopSession()`, `getSessionSummary()` |
| `media.js` | `startMediaCapture()`, `stopMediaCapture()` |
| `signals.js` | `connectSignals()`, `disconnectSignals()` |
| `ui.js` | `formatTime()`, `updateSignalDisplay()`, `storeSessionData()` |

---

## Data Flow

```
┌────────────┐     POST /api/session/start     ┌────────────┐
│  Landing   │ ──────────────────────────────▶ │  Backend   │
│   Page     │                                 │   API      │
└────────────┘                                 └────────────┘
      │                                              │
      │ Navigate to /capture                         │ Create CaptureSession
      ▼                                              ▼
┌────────────┐     WebSocket /api/session/live ┌────────────┐
│  Capture   │ ◀─────────────────────────────▶ │  Capture   │
│   Page     │        Live signal stream       │  Session   │
└────────────┘                                 └────────────┘
      │                                              │
      │ POST /api/session/stop                       │ Save files
      ▼                                              ▼
┌────────────┐     GET /api/session/summary    ┌────────────┐
│  Summary   │ ◀────────────────────────────── │   Data     │
│   Page     │                                 │  Output    │
└────────────┘                                 └────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve landing page |
| GET | `/capture` | Serve capture page |
| GET | `/summary` | Serve summary page |
| POST | `/api/session/start` | Start capture session |
| POST | `/api/session/stop` | Stop capture session |
| GET | `/api/session/summary` | Get session summary |
| WS | `/api/session/live` | Live signal stream |
| GET | `/api/health` | Health check |

---

## Signal Types Captured

### Visual Signals
- **Face Detected** - Boolean presence of face
- **Eye Direction** - left / center / right
- **Head Movement** - low / medium / high
- **Blink Events** - Detected via Eye Aspect Ratio

### Audio Signals
- **Voice Activity** - active / silent
- **Speaking Duration** - Cumulative time

### Integrity Signals
- **Face Continuous** - >90% face presence
- **Multiple Faces** - Detected intrusion
- **Audio Interruptions** - Background noise events

---

## Running the Application

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start server
python -m uvicorn app.main:app --reload --port 8000

# Open browser
# http://localhost:8000
```

---

## Demo vs Production

| Aspect | Demo (Current) | Production |
|--------|----------------|------------|
| Storage | Local `data/` folder | Cloud storage |
| Analysis | None - raw signals only | Real-time ML pipeline |
| Frontend | CDN Tailwind, vanilla JS | React/Vue + bundler |
| Auth | None | OAuth/SSO |
| Deployment | Local uvicorn | Kubernetes/Cloud Run |

---

*This demo captures raw visual and audio signals only. No AI analysis, scoring, or hiring decisions are performed.*
