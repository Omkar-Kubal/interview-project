# Signal Capture Backend

Backend service for the AI Interview Signal Capture system. This module handles multimodal signal acquisition from candidates including video, audio, face tracking, and voice activity detection.

## Architecture

This component represents the **Signal Ingestion Layer** of the interview system:

```
signal-capture-backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── cli.py               # Command-line interface
│   ├── api/                 # HTTP & WebSocket routes
│   │   └── session.py       # Session management
│   ├── capture/             # Signal acquisition
│   │   ├── camera/          # Video + face analysis
│   │   └── audio/           # Audio + voice detection
│   ├── session/             # Session lifecycle
│   └── ui/                  # CLI overlay (optional)
├── data/                    # Output directory
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
cd signal-capture-backend
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`

### 3. (Optional) Run CLI Mode

For standalone capture without the web interface:

```bash
python -m app.cli
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session/start` | Start a new capture session |
| POST | `/api/session/stop` | Stop the current session |
| GET | `/api/session/summary` | Get session summary |
| WS | `/api/session/live` | WebSocket for live signals |
| GET | `/api/health` | Health check |

## Output

Captured data is saved to `data/user_<candidate_id>/`:
- `video.mp4` - Video recording
- `audio.wav` - Audio recording
- `face_log.json` - Face detection events
- `audio_log.json` - Voice activity events

## Demo vs Product

This is a **demo component** for signal capture. In production:
- Signals would stream to a processing pipeline
- No local video/audio storage
- Real-time analysis would be performed

---

*This demo captures raw signals only. No AI analysis, scoring, or hiring decisions are performed.*
