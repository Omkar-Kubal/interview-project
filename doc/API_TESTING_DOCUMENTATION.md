# AI Interview System - API Testing Documentation

**Version:** 1.0.0  
**Last Updated:** 2026-02-05  
**Test Suite Location:** `backend/tests/test_api_endpoints.py`

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Environment Setup](#test-environment-setup)
3. [API Endpoints Overview](#api-endpoints-overview)
4. [Detailed Test Scenarios](#detailed-test-scenarios)
5. [Test Results Summary](#test-results-summary)
6. [Security Testing](#security-testing)
7. [Known Issues & Recommendations](#known-issues--recommendations)

---

## Executive Summary

This document provides comprehensive end-to-end testing documentation for the AI Interview System API. The test suite covers all **40 endpoint tests** across 6 major categories:

| Category | Tests | Status |
|----------|-------|--------|
| Authentication | 9 | ✅ All Passed |
| Jobs API | 7 | ✅ All Passed |
| Applications API | 4 | ✅ All Passed |
| Questions API | 5 | ✅ All Passed |
| Session API | 4 | ✅ All Passed |
| Static Pages | 8 | ✅ All Passed |
| Security Features | 3 | ✅ All Passed |

**Overall Result: 40/40 Tests Passed (100%)**

---

## Test Environment Setup

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx requests

# Ensure application dependencies are installed
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all API tests
cd backend
python -m pytest tests/test_api_endpoints.py -v --asyncio-mode=auto

# Run specific test category
python -m pytest tests/test_api_endpoints.py::TestAuthentication -v

# Run with detailed output
python -m pytest tests/test_api_endpoints.py -v --tb=long
```

### Test Configuration

| Setting | Value |
|---------|-------|
| Base URL | `http://test` (ASGI test client) |
| Database | SQLite (`interview.db`) |
| Auth Tokens | 24-hour access tokens, 7-day refresh tokens |
| Default Admin | `admin@example.com` / `admin123` |

---

## API Endpoints Overview

### 1. Authentication Endpoints (`/api/auth/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/auth/register` | POST | No | Register new user (seeker/recruiter) |
| `/api/auth/login` | POST | No | Login and receive JWT tokens |
| `/api/auth/refresh` | POST | No | Refresh access token |
| `/api/auth/profile/{user_id}` | GET | No | Get user profile |

### 2. Jobs Endpoints (`/api/jobs/`)

| Endpoint | Method | Auth Required | Role | Description |
|----------|--------|---------------|------|-------------|
| `/api/jobs/` | GET | No | Any | List all active jobs |
| `/api/jobs/` | POST | Yes | Recruiter/Admin | Create new job |
| `/api/jobs/{job_id}` | GET | No | Any | Get job details |
| `/api/jobs/recruiter/{recruiter_id}` | GET | Yes | Recruiter/Admin | List recruiter's jobs |

### 3. Applications Endpoints (`/api/applications/`)

| Endpoint | Method | Auth Required | Role | Description |
|----------|--------|---------------|------|-------------|
| `/api/applications/apply` | POST | Yes | Seeker | Apply to a job |
| `/api/applications/me` | GET | Yes | Seeker | List own applications |
| `/api/applications/job/{job_id}` | GET | Yes | Recruiter/Admin | List job applications |
| `/api/applications/{id}/status` | PATCH | Yes | Recruiter/Admin | Update application status |
| `/api/applications/{id}/sessions` | GET | Yes | Any (owned) | Get interview sessions |

### 4. Questions Endpoints (`/api/questions/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/questions/domains` | GET | No | List question domains |
| `/api/questions/domain/{domain}` | GET | No | Get questions by domain |
| `/api/questions/job/{job_id}` | GET | Yes | Get job questionnaire |
| `/api/questions/answer/text` | POST | Yes | Submit text/MCQ answer |
| `/api/questions/answer/media` | POST | Yes | Submit video/audio answer |
| `/api/questions/answers/{application_id}` | GET | Yes | Get application answers |
| `/api/questions/answers/{answer_id}/score` | PATCH | Yes | Score an answer (recruiter) |

### 5. Session Endpoints (`/api/session/`)

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/session/start` | POST | Yes | Start capture session |
| `/api/session/stop` | POST | Yes | Stop capture session |
| `/api/session/heartbeat` | POST | Yes | Update session heartbeat |
| `/api/session/summary` | GET | Yes | Get session summary |
| `/api/session/live` | WebSocket | No | Live signal stream |

### 6. Utility Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/health` | GET | No | Health check |
| `/video_feed` | GET | No | MJPEG video stream |

### 7. Static Pages

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/login` | GET | Login page |
| `/register` | GET | Registration page |
| `/jobs` | GET | Job board page |
| `/apply` | GET | Job application page |
| `/dashboard` | GET | Candidate dashboard |
| `/admin` | GET | Admin/Recruiter panel |
| `/capture` | GET | Live capture page |
| `/interview` | GET | Interview questionnaire |
| `/review` | GET | Review answers page |
| `/replay` | GET | Session replay page |
| `/summary` | GET | Session summary page |

---

## Detailed Test Scenarios

### Authentication Tests

#### Test 1: Health Check
```
Endpoint: GET /api/health
Expected: 200 OK with {"status": "healthy"}
Result: ✅ PASSED
```

#### Test 2: User Registration (Seeker)
```
Endpoint: POST /api/auth/register
Payload: {
  "email": "testseeker@test.com",
  "password": "TestPass123",
  "full_name": "Test Seeker",
  "role": "seeker"
}
Expected: 200 OK with user_id
Result: ✅ PASSED
```

#### Test 3: User Registration (Recruiter)
```
Endpoint: POST /api/auth/register
Payload: {
  "email": "testrecruiter@test.com",
  "password": "TestPass123",
  "full_name": "Test Recruiter",
  "role": "recruiter"
}
Expected: 200 OK with user_id
Result: ✅ PASSED
```

#### Test 4: Password Validation
```
Endpoint: POST /api/auth/register
Test Cases:
  - Password "short" → 422 (too short)
  - Password "nouppercase123" → 422 (missing uppercase)
  - Password "NOLOWERCASE123" → 422 (missing lowercase)
  - Password "NoDigitsHere" → 422 (missing digit)
Result: ✅ PASSED (all validation rules enforced)
```

#### Test 5: Duplicate Email Rejection
```
Endpoint: POST /api/auth/register
Scenario: Register with already-existing email
Expected: 400 Bad Request
Result: ✅ PASSED
```

#### Test 6: Successful Login
```
Endpoint: POST /api/auth/login
Payload: username=admin@example.com&password=admin123
Expected: 200 OK with {access_token, refresh_token, token_type, user}
Result: ✅ PASSED
```

#### Test 7: Invalid Login Credentials
```
Endpoint: POST /api/auth/login
Payload: username=admin@example.com&password=wrongpassword
Expected: 401 Unauthorized
Result: ✅ PASSED
```

#### Test 8: Get User Profile
```
Endpoint: GET /api/auth/profile/{user_id}
Expected: 200 OK with user details
Result: ✅ PASSED
```

#### Test 9: Token Refresh
```
Endpoint: POST /api/auth/refresh
Payload: {"refresh_token": "<valid_refresh_token>"}
Expected: 200 OK with new access_token
Result: ✅ PASSED
```

---

### Jobs API Tests

#### Test 10: List Jobs (Public)
```
Endpoint: GET /api/jobs/
Expected: 200 OK with array of active jobs
Result: ✅ PASSED
```

#### Test 11: Create Job as Recruiter
```
Endpoint: POST /api/jobs/
Auth: Recruiter JWT token
Payload: {
  "title": "AI Engineer Test Position",
  "description": "Test job posting",
  "location": "Remote",
  "salary_range": "$100k-$150k"
}
Expected: 200 OK with created job
Result: ✅ PASSED
```

#### Test 12: Create Job as Admin
```
Endpoint: POST /api/jobs/
Auth: Admin JWT token
Expected: 200 OK
Result: ✅ PASSED
```

#### Test 13: Create Job as Seeker (Unauthorized)
```
Endpoint: POST /api/jobs/
Auth: Seeker JWT token
Expected: 403 Forbidden
Result: ✅ PASSED
```

#### Test 14: Get Job by ID
```
Endpoint: GET /api/jobs/{job_id}
Expected: 200 OK with job details
Result: ✅ PASSED
```

#### Test 15: Get Non-Existent Job
```
Endpoint: GET /api/jobs/99999
Expected: 404 Not Found
Result: ✅ PASSED
```

#### Test 16: List Recruiter's Jobs
```
Endpoint: GET /api/jobs/recruiter/{recruiter_id}
Auth: Recruiter JWT token
Expected: 200 OK with array of recruiter's jobs
Result: ✅ PASSED
```

---

### Applications API Tests

#### Test 17: Apply to Job
```
Endpoint: POST /api/applications/apply
Auth: Seeker JWT token
Payload: job_id, seeker_id (form data)
Expected: 200 OK or 400 if already applied
Result: ✅ PASSED
```

#### Test 18: List My Applications
```
Endpoint: GET /api/applications/me?seeker_id={id}
Auth: Seeker JWT token
Expected: 200 OK with array of applications
Result: ✅ PASSED
```

#### Test 19: List Job Applications (Recruiter)
```
Endpoint: GET /api/applications/job/{job_id}
Auth: Admin JWT token
Expected: 200 OK with array of applications
Result: ✅ PASSED
```

#### Test 20: Update Application Status
```
Endpoint: PATCH /api/applications/{id}/status
Auth: Admin JWT token
Payload: {"status": "Interview Required"}
Expected: 200 OK with updated application
Result: ✅ PASSED
```

---

### Questions API Tests

#### Test 21: List Question Domains
```
Endpoint: GET /api/questions/domains
Expected: 200 OK with array of domain strings
Result: ✅ PASSED
```

#### Test 22: Get Questions by Domain
```
Endpoint: GET /api/questions/domain/{domain}
Domains tested: AI-ML, Fullstack, Cybersecurity
Expected: 200 OK with array of questions
Result: ✅ PASSED
```

#### Test 23: Get Job Questionnaire
```
Endpoint: GET /api/questions/job/{job_id}
Auth: Seeker JWT token
Expected: 200 OK or 404 if no questionnaire
Result: ✅ PASSED
```

#### Test 24: Submit Text Answer
```
Endpoint: POST /api/questions/answer/text
Auth: Seeker JWT token
Payload: {application_id, question_id, answer_text}
Expected: 200 OK or 404 if question doesn't exist
Result: ✅ PASSED
```

#### Test 25: Get Application Answers
```
Endpoint: GET /api/questions/answers/{application_id}
Auth: Seeker JWT token
Expected: 200 OK with array of answers
Result: ✅ PASSED
```

---

### Session API Tests

#### Test 26-29: Session Endpoints Require Authentication
```
Endpoints:
  - POST /api/session/start
  - POST /api/session/stop
  - POST /api/session/heartbeat
  - GET /api/session/summary
Expected: 401 Unauthorized without auth token
Result: ✅ ALL PASSED
```

---

### Static Pages Tests

#### Tests 30-37: All Static Pages Load Successfully
```
Pages Tested:
  - / (Root) → ✅ 200 OK
  - /login → ✅ 200 OK
  - /register → ✅ 200 OK
  - /jobs → ✅ 200 OK
  - /dashboard → ✅ 200 OK
  - /admin → ✅ 200 OK
  - /interview → ✅ 200 OK
  - /review → ✅ 200 OK
Result: ✅ ALL PASSED
```

---

### Security Tests

#### Test 38: CSRF Protection
```
Endpoint: POST /api/auth/register
Scenario: JSON POST without X-Requested-With header
Expected: 403 Forbidden (CSRF validation failed)
Result: ✅ PASSED
```

#### Test 39: Role-Based Access Control
```
Endpoint: POST /api/jobs/
Auth: Seeker JWT token
Expected: 403 Forbidden (seekers cannot create jobs)
Result: ✅ PASSED
```

#### Test 40: Invalid Token Rejection
```
Endpoint: GET /api/applications/me
Auth: "Bearer invalid_token_here"
Expected: 401 Unauthorized
Result: ✅ PASSED
```

---

## Test Results Summary

### Overall Statistics

```
================================================================================
                    AI INTERVIEW SYSTEM - API TEST REPORT
================================================================================

Generated: 2026-02-05 21:10:00
Total Tests Run: 40
Passed: 40 | Failed: 0 | Skipped: 0 | Warnings: 3

--------------------------------------------------------------------------------
RESULTS BY CATEGORY:
--------------------------------------------------------------------------------

### Authentication
  ✅ [GET] /api/health - Status: 200
  ✅ [POST] /api/auth/register - Seeker registration - Status: 200
  ✅ [POST] /api/auth/register - Recruiter registration - Status: 200
  ✅ [POST] /api/auth/register - Password validation (all 4 rules enforced)
  ✅ [POST] /api/auth/register - Duplicate email rejection - Status: 400
  ✅ [POST] /api/auth/login - Admin login - Status: 200
  ✅ [POST] /api/auth/login - Invalid credentials rejection - Status: 401
  ✅ [GET] /api/auth/profile/{id} - Status: 200
  ✅ [POST] /api/auth/refresh - Token refresh - Status: 200

### Jobs
  ✅ [GET] /api/jobs/ - List jobs - Status: 200
  ✅ [POST] /api/jobs/ - Create job as recruiter - Status: 200
  ✅ [POST] /api/jobs/ - Create job as admin - Status: 200
  ✅ [POST] /api/jobs/ - Seeker job creation rejection - Status: 403
  ✅ [GET] /api/jobs/{id} - Status: 200
  ✅ [GET] /api/jobs/99999 - Job not found - Status: 404
  ✅ [GET] /api/jobs/recruiter/{id} - Status: 200

### Applications
  ✅ [POST] /api/applications/apply - Apply to job - Status: 200
  ✅ [GET] /api/applications/me - List my applications - Status: 200
  ✅ [GET] /api/applications/job/{id} - Status: 200
  ✅ [PATCH] /api/applications/{id}/status - Update status - Status: 200

### Questions
  ✅ [GET] /api/questions/domains - Status: 200
  ✅ [GET] /api/questions/domain/{domain} - Status: 200
  ✅ [GET] /api/questions/job/{id} - Status: 200/404
  ✅ [POST] /api/questions/answer/text - Submit answer - Status: 200/404
  ✅ [GET] /api/questions/answers/{id} - Get answers - Status: 200

### Session
  ✅ [POST] /api/session/start - Auth required - Status: 401
  ✅ [POST] /api/session/stop - Auth required - Status: 401
  ✅ [POST] /api/session/heartbeat - Auth required - Status: 401
  ✅ [GET] /api/session/summary - Auth required - Status: 401

### Static Pages
  ✅ [GET] / - Root page - Status: 200
  ✅ [GET] /login - Login page - Status: 200
  ✅ [GET] /register - Register page - Status: 200
  ✅ [GET] /jobs - Jobs page - Status: 200
  ✅ [GET] /dashboard - Dashboard page - Status: 200
  ✅ [GET] /admin - Admin page - Status: 200
  ✅ [GET] /interview - Interview page - Status: 200
  ✅ [GET] /review - Review page - Status: 200

### Security
  ✅ [POST] /api/auth/register - CSRF protection - Status: 403
  ✅ [POST] /api/jobs/ [RBAC] - Role-based access control - Status: 403
  ✅ [GET] /api/applications/me [Invalid Token] - Invalid token rejection - Status: 401

================================================================================
                              END OF REPORT
================================================================================
```

---

## Known Issues & Recommendations

### Deprecation Warnings

1. **Pydantic Config Class** (Low Priority)
   - File: `app/api/questions.py:29`
   - Issue: Class-based `config` is deprecated in Pydantic V2
   - Fix: Use `model_config = ConfigDict(from_attributes=True)` instead

2. **FastAPI on_event** (Medium Priority)
   - File: `app/main.py:324`
   - Issue: `on_event` decorator is deprecated
   - Fix: Use lifespan event handlers instead

### Security Recommendations

1. ✅ **CSRF Protection** - Implemented and tested
2. ✅ **Role-Based Access Control** - Implemented and tested
3. ✅ **JWT Token Validation** - Implemented and tested
4. ✅ **Password Strength Validation** - Implemented and tested
5. ⚠️ **Rate Limiting** - Not implemented (recommended for production)
6. ⚠️ **Input Sanitization** - Basic validation exists, consider adding more thorough sanitization

### Performance Considerations

1. ✅ **Job Listings Cache** - 60-second TTL cache implemented
2. ⚠️ **Database Connection Pooling** - Using SQLite, consider PostgreSQL for production
3. ⚠️ **Session Cleanup** - Background task runs every 10 seconds with 1-minute timeout

---

## Appendix A: Request/Response Examples

### Authentication Flow

```http
# 1. Register
POST /api/auth/register
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
  "email": "newuser@example.com",
  "password": "SecurePass123",
  "full_name": "New User",
  "role": "seeker"
}

# Response 200 OK
{
  "status": "success",
  "user_id": 5
}

# 2. Login
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

username=newuser@example.com&password=SecurePass123

# Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "email": "newuser@example.com",
    "full_name": "New User",
    "role": "seeker"
  }
}

# 3. Use Protected Endpoint
GET /api/applications/me?seeker_id=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# Response 200 OK
[
  {
    "id": 1,
    "job_id": 1,
    "seeker_id": 5,
    "status": "Applied",
    "created_at": "2026-02-05T21:00:00"
  }
]
```

### Job Creation Flow

```http
# Create Job (Recruiter/Admin only)
POST /api/jobs/
Authorization: Bearer <recruiter_token>
Content-Type: application/json
X-Requested-With: XMLHttpRequest

{
  "title": "Senior Developer",
  "description": "Full-stack position",
  "location": "Remote",
  "salary_range": "$120k-$180k",
  "is_active": true,
  "recruiter_id": 2
}

# Response 200 OK
{
  "id": 3,
  "title": "Senior Developer",
  "description": "Full-stack position",
  "location": "Remote",
  "salary_range": "$120k-$180k",
  "is_active": true,
  "recruiter_id": 2,
  "created_at": "2026-02-05T21:05:00"
}
```

---

## Appendix B: Error Response Formats

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Recruiter/Admin permissions required"
}
```

### 404 Not Found
```json
{
  "detail": "Job not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "password"],
      "msg": "Value error, Password must be at least 8 characters long"
    }
  ]
}
```

---

**Document End**
