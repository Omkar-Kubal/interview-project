# Implementation Plan: Career Portal & AI Interview Management System

This plan outlines the roadmap for building the full Career Portal, integrating the existing **AI Signal Capture** module into a complete Candidate/Admin ecosystem.

## Project Overview
- **Backend**: FastAPI, SQLModel (SQLite), JWT Authentication.
- **Frontend**: Vanilla JS, Tailwind CSS, Responsive Design.
- **Core Features**: Candidate Auth, Job Board, Application Tracking, AI Interview Capture, and Admin Session Analytics.

---

## Phase 1: Database Schema & Migration
Establish the foundation using SQLModel.
- [ ] **Models Definition**:
    - `User`: id, email, password_hash, full_name, role (candidate/admin), created_at.
    - `Job`: id, title, description, location, salary_range, status (open/closed).
    - `Application`: id, user_id, job_id, resume_path, status (applied, interviewed, rejected).
    - `InterviewSession`: id, application_id, start_time, end_time, result_json_mapping (links to data/interviews/).
- [ ] **Database Init**: Script to create tables and seed one Admin user and 2-3 sample Jobs.

## Phase 2: Authentication & User Management
Secure the application and handle candidate profiles.
- [ ] **JWT Implementation**: Sign-in/Sign-up logic with `passlib` for hashing and `python-jose` for tokens.
- [ ] **Auth Endpoints**:
    - `POST /api/auth/register`
    - `POST /api/auth/login`
- [ ] **Frontend Pages**:
    - `login.html`: Premium dark-themed login interface.
    - `register.html`: Multi-step signup form.

## Phase 3: Job Board & Application Flow
The core candidate experience.
- [ ] **Job APIs**:
    - `GET /api/jobs`: List all active jobs.
    - `GET /api/jobs/{id}`: Job detail view.
- [ ] **Application Logic**:
    - `POST /api/applications/apply`: Handle resume upload and link user to job.
- [ ] **Frontend Pages**:
    - `dashboard.html`: Candidate home showing applied jobs.
    - `jobs.html`: Searchable job board.

## Phase 4: Interview Integration
Connecting the existing Capture Module to the database.
- [ ] **Session Linking**: Modify `CaptureSession.stop()` to link the generated `session_id` to a specific `Application` record in the database.
- [ ] **Capture Entry Point**: Ensure the `/capture` page only opens if a valid application exists.
- [ ] **Video Persistence**: Finalize the moving of recorded files from temporary paths to organized storage.

## Phase 5: Admin Dashboard & Analytics
Reviewing the captured AI signals.
- [ ] **Admin APIs**:
    - `GET /api/admin/sessions`: List all completed interviews with integrity flags.
    - `GET /api/admin/sessions/{id}`: Retrieve full telemetry (face logs, eye logs, audio logs).
- [ ] **Session Player**: 
    - Build a custom video player UI that syncs the recorded `.mp4` with the `.json` telemetry logs for replay.

## Phase 6: Final Polish & Deployment
- [ ] **UI Sync**: Ensure the "Science" design language is consistent across every page.
- [ ] **Production Readiness**: Configure `gunicorn` for deployment and finalize `.env` management.
- [ ] **Documentation**: Complete the `README.md` with setup instructions.

---

## Technical Stack Recap
- **Data Layer**: SQLModel + SQLite
- **Auth**: OAuth2 Password Flow + JWT
- **Capture**: OpenCV + MediaPipe + SoundDevice
- **Frontend**: Tailwind (CDN) + Vanilla JS (ES6 Modules)
