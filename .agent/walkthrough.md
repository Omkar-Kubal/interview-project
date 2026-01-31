# Project Walkthrough: AI Interview Signal Capture

Welcome to the **AI Interview Signal Capture** system. This project is a specialized "Signal Ingestion Layer" designed to capture high-fidelity multimodal data (video, audio, and behavioral signals) from candidates during an interview process.

## 🏗 Overall Architecture

The project follows a decoupled architecture, though for simplicity in this demo, the backend serves the frontend:

- **Frontend**: A pure HTML/JS application located in `/frontend`. It handles candidate interactions and displays live feedback.
- **Backend**: A FastAPI server in `/backend` that performs heavy lifting: video/audio capture, real-time face tracking with MediaPipe, and session management.
- **Database**: SQLite (managed via SQLModel) stores user profiles, job listings, and session metadata.

---

## 🛠 Backend Deep Dive

### 1. Signal Capture Engine (`/backend/app/capture`)
This is the heart of the system. It consists of two main streams:
- **Camera Module**: Uses OpenCV for frame acquisition and **MediaPipe** for real-time face detection. It tracks eye direction, head movement, and blinks.
- **Audio Module**: Uses `sounddevice` to capture audio and performs basic Voice Activity Detection (VAD) to log when the candidate is speaking.

### 2. Session Lifecycle (`/backend/app/api/session.py`)
Sessions are managed as stateful objects.
- **Start**: When a session starts, it creates a unique directory in `backend/data/user_<id>/<uuid>/`.
- **Active**: While active, it streams data to disk and calculates "integrity signals" (e.g., is the face continuously detected? Are multiple faces present?).
- **Stop**: On stop, it flushes files, generates a summary, and persists the metadata to the database.

### 3. API & WebSockets (`/backend/app/main.py`)
- **MJPEG Stream**: The `/video_feed` endpoint provides a live MJPEG stream of the camera feed (with optional overlays) to the frontend.
- **WebSocket**: The `/api/session/live` endpoint broadcasts real-time JSON signals (blinks, head position, VAD) at ~5Hz to update the frontend UI.

---

## 🎨 Frontend Deep Dive

The frontend is built with modularity in mind without the overhead of a framework (for demo clarity):

- **Modular JS**: 
    - `media.js`: Handles browser-side camera/mic permissions and visual feedback.
    - `signals.js`: Connects to the backend WebSocket to display real-time telemetry.
    - `session.js`: Handles start/stop logic and interaction with the FastAPI and jobs API.
- **UX Strategy**: 
    - **Permission Timing**: Camera access is *only* requested once the candidate enters the `/capture` page, ensuring a professional and non-intrusive greeting.
    - **Live Telemetry**: Candidates see real-time indicators of their signals, which serves as a "feedback loop" for their setup (e.g., "Face Detected" vs "Face Lost").

---

## 💾 Data Persistence

All raw data is stored locally for this demo:
- **`video.mp4`**: Raw candidate video.
- **`audio.wav`**: Raw candidate audio.
- **`face_log.json`**: Time-series data of facial events (blinks, eye movement).
- **`audio_log.json`**: Time-series data of VAD events.
- **`interview.db`**: SQLite database containing the structural relationships (Jobs -> Applications -> Sessions).

---

## 🚀 Key Features

1.  **Integrity Checks**: Detects if a candidate leaves the frame or if another person appears.
2.  **Multimodal Sync**: Correlates facial expressions with voice activity.
3.  **Real-time Feedback**: Provides a "confidence score" for the capture quality in real-time.
4.  **Admin Replay**: Recruiters can review sessions with synchronized signal overlays (planned feature in the UI).

---

## 📂 Folder Summary

```text
/
├── backend/
│   ├── app/           # FastAPI application logic
│   ├── data/          # Captured video/audio/logs (ignored by git)
│   ├── interview.db   # Local database
│   └── requirements.txt
├── frontend/
│   ├── pages/         # HTML templates
│   ├── scripts/       # Modular JS logic
│   ├── styles/        # CSS
│   └── config.js      # API endpoints configuration
└── doc/               # Design and implementation docs
```
