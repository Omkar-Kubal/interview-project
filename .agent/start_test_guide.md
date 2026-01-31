# 🚀 Start & Test Walkthrough

This guide will take you through setting up, running, and testing the **AI Interview Signal Capture** system from scratch.

---

## 1. Setup the Environment

Ensure you are in the project root (`d:\interview-project`).

### **Install Dependencies**
The backend requires several libraries for signal processing and the web server.

```powershell
cd backend
# Create a virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

## 2. Launch the Project

The backend serves both the API and the Frontend.

```powershell
# Run from the /backend directory
python -m uvicorn app.main:app --reload --port 8000
```

Once started, you should see:
`INFO: Uvicorn running on http://127.0.0.1:8000`

---

## 3. Testing the Main User Flow

Follow these steps to test the end-to-end signal capture:

### **Step A: Access the Landing Page**
1. Open your browser and go to `http://localhost:8000`.
2. Enter any **Candidate ID** (e.g., `TEST_USER_01`).
3. Click **"Begin Capture"**.

### **Step B: Live Capture Page**
1. You will be redirected to `/capture`.
2. **Grant Permissions**: The browser will ask for Camera and Microphone access. 
3. **Check the Feed**: You should see your camera feed in the center.
4. **Observe Signals**:
   - Look for the **"Face Detected"** status to turn green.
   - Try blinking or moving your head; the telemetry panel on the right should update in real-time.
   - Speak a few words; watch the **Voice Activity** indicator.

### **Step C: End Session**
1. Click **"End Session"**.
2. You will be redirected to the **Summary Page** (`/summary`).
3. View the session stats (Duration, Integrity Flags).

---

## 4. Testing the Recruitment Flow (Admin)

The system includes a pre-seeded admin account to view all results.

1. Go to `http://localhost:8000/login`.
2. Login with credentials:
   - **Email**: `admin@example.com`
   - **Password**: `admin123`
3. Navigate to the **Admin Console** (`/admin`).
4. You should see a list of applications and the session you just recorded.

---

## 5. Verifying Data Logs

After testing, check your local filesystem to ensure data was saved correctly:

- Navigate to `backend/data/user_TEST_USER_01/`.
- Inside the timestamped folder, you should find:
  - `video.mp4` & `audio.wav`: The raw media recordings.
  - `face_log.json`: The time-series tracking data.
  - `audio_log.json`: The voice activity durations.

---

## 🛠 Troubleshooting

- **Camera not appearing?** Close other apps using your camera (Teams, Zoom, etc.) and refresh the page.
- **No signals?** Ensure you are in a well-lit area. The MediaPipe face tracker needs a clear view of your eyes and nose.
- **Database errors?** If `interview.db` gets corrupted, you can delete it and restart the server; it will automatically recreate and seed the database.
