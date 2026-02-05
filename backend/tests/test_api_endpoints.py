"""
Comprehensive End-to-End API Test Suite for AI Interview System

This script tests all API endpoints across the project:
- Authentication (register, login, refresh, profile)
- Jobs (create, list, get by ID, list by recruiter)
- Applications (apply, list, update status, get sessions)
- Questions (domains, questions by domain, job questionnaire, submit answers, review)
- Sessions (start, stop, heartbeat, summary)
- Health checks

Requires: pytest, httpx, requests
Run with: python -m pytest tests/test_api_endpoints.py -v --tb=short
Or standalone: python tests/test_api_endpoints.py
"""
import pytest
from httpx import AsyncClient, ASGITransport
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.persistence.database import engine, init_db
from sqlmodel import SQLModel, Session, select


# ============ TEST CONFIGURATION ============
BASE_URL = "http://test"
TEST_RESULTS = []

# Test data
TEST_SEEKER = {
    "email": f"testseeker_{datetime.now().strftime('%H%M%S')}@test.com",
    "password": "TestPass123",
    "full_name": "Test Seeker",
    "role": "seeker"
}

TEST_RECRUITER = {
    "email": f"testrecruiter_{datetime.now().strftime('%H%M%S')}@test.com",
    "password": "TestPass123",
    "full_name": "Test Recruiter", 
    "role": "recruiter"
}

TEST_JOB = {
    "title": "AI Engineer Test Position",
    "description": "A test job posting for the QA suite",
    "location": "Remote",
    "salary_range": "$100k - $150k",
    "is_active": True
}


def log_result(endpoint: str, method: str, status: str, details: str = ""):
    """Log test result for documentation."""
    result = {
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{status_icon} [{method}] {endpoint} - {status} {details}")


# ============ FIXTURES ============
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
async def admin_token(async_client):
    """Get admin token using seeded credentials."""
    response = await async_client.post(
        "/api/auth/login",
        data={"username": "admin@example.com", "password": "admin123"},
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.fixture(scope="session")
async def seeker_data(async_client):
    """Register a seeker and return credentials + token."""
    # Register
    response = await async_client.post(
        "/api/auth/register",
        json=TEST_SEEKER,
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    data = {"registration": response.json() if response.status_code == 200 else None}
    
    # Login
    if response.status_code == 200:
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": TEST_SEEKER["email"], "password": TEST_SEEKER["password"]},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        if login_response.status_code == 200:
            data["token"] = login_response.json()["access_token"]
            data["refresh_token"] = login_response.json()["refresh_token"]
            data["user"] = login_response.json()["user"]
    
    return data


@pytest.fixture(scope="session")
async def recruiter_data(async_client):
    """Register a recruiter and return credentials + token."""
    # Register
    response = await async_client.post(
        "/api/auth/register",
        json=TEST_RECRUITER,
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    data = {"registration": response.json() if response.status_code == 200 else None}
    
    # Login
    if response.status_code == 200:
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": TEST_RECRUITER["email"], "password": TEST_RECRUITER["password"]},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        if login_response.status_code == 200:
            data["token"] = login_response.json()["access_token"]
            data["refresh_token"] = login_response.json()["refresh_token"]
            data["user"] = login_response.json()["user"]
    
    return data


# ============ AUTHENTICATION TESTS ============
class TestAuthentication:
    """Test Authentication API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test /api/health endpoint."""
        response = await async_client.get("/api/health")
        log_result("/api/health", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Status: {response.status_code}")
        assert response.status_code == 200
        assert "status" in response.json()
    
    @pytest.mark.asyncio
    async def test_register_seeker(self, async_client):
        """Test /api/auth/register - Seeker registration."""
        test_user = {
            "email": f"newseeker_{datetime.now().strftime('%H%M%S%f')}@test.com",
            "password": "Password123",
            "full_name": "New Test Seeker",
            "role": "seeker"
        }
        response = await async_client.post(
            "/api/auth/register",
            json=test_user,
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        log_result("/api/auth/register", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Seeker registration - Status: {response.status_code}")
        assert response.status_code == 200
        assert "user_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_register_recruiter(self, async_client):
        """Test /api/auth/register - Recruiter registration."""
        test_user = {
            "email": f"newrecruiter_{datetime.now().strftime('%H%M%S%f')}@test.com",
            "password": "Password123",
            "full_name": "New Test Recruiter",
            "role": "recruiter"
        }
        response = await async_client.post(
            "/api/auth/register",
            json=test_user,
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        log_result("/api/auth/register", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Recruiter registration - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_register_password_validation(self, async_client):
        """Test password validation (min 8 chars, upper, lower, digit)."""
        weak_passwords = [
            ("short", "Too short"),
            ("nouppercase123", "Missing uppercase"),
            ("NOLOWERCASE123", "Missing lowercase"),
            ("NoDigitsHere", "Missing digit")
        ]
        
        for pwd, reason in weak_passwords:
            test_user = {
                "email": f"weakpwd_{datetime.now().strftime('%H%M%S%f')}@test.com",
                "password": pwd,
                "full_name": "Weak Password Test",
                "role": "seeker"
            }
            response = await async_client.post(
                "/api/auth/register",
                json=test_user,
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            # Should fail validation (422)
            expected = response.status_code == 422
            log_result("/api/auth/register", "POST", "PASS" if expected else "FAIL",
                      f"Password validation ({reason}) - Status: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client, seeker_data):
        """Test duplicate email registration rejection."""
        response = await async_client.post(
            "/api/auth/register",
            json=TEST_SEEKER,
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        expected = response.status_code == 400
        log_result("/api/auth/register", "POST", "PASS" if expected else "FAIL",
                  f"Duplicate email rejection - Status: {response.status_code}")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client):
        """Test /api/auth/login - Successful login."""
        response = await async_client.post(
            "/api/auth/login",
            data={"username": "admin@example.com", "password": "admin123"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        log_result("/api/auth/login", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Admin login - Status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client):
        """Test login with invalid credentials."""
        response = await async_client.post(
            "/api/auth/login",
            data={"username": "admin@example.com", "password": "wrongpassword"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        expected = response.status_code == 401
        log_result("/api/auth/login", "POST", "PASS" if expected else "FAIL",
                  f"Invalid credentials rejection - Status: {response.status_code}")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_profile(self, async_client, seeker_data):
        """Test /api/auth/profile/{user_id} endpoint."""
        user_id = seeker_data["user"]["id"]
        response = await async_client.get(f"/api/auth/profile/{user_id}")
        log_result(f"/api/auth/profile/{user_id}", "GET", 
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Status: {response.status_code}")
        assert response.status_code == 200
        assert response.json()["email"] == TEST_SEEKER["email"]
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, async_client, seeker_data):
        """Test /api/auth/refresh - Token refresh."""
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": seeker_data["refresh_token"]},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        log_result("/api/auth/refresh", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Token refresh - Status: {response.status_code}")
        assert response.status_code == 200
        assert "access_token" in response.json()


# ============ JOBS API TESTS ============
class TestJobsAPI:
    """Test Jobs API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_jobs_public(self, async_client):
        """Test GET /api/jobs - List all active jobs (public)."""
        response = await async_client.get("/api/jobs/")
        log_result("/api/jobs/", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"List jobs - Status: {response.status_code}, Count: {len(response.json()) if response.status_code == 200 else 0}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_create_job_as_recruiter(self, async_client, recruiter_data):
        """Test POST /api/jobs/ - Create job as recruiter."""
        job_data = TEST_JOB.copy()
        job_data["recruiter_id"] = recruiter_data["user"]["id"]
        
        response = await async_client.post(
            "/api/jobs/",
            json=job_data,
            headers={
                "Authorization": f"Bearer {recruiter_data['token']}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        log_result("/api/jobs/", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Create job as recruiter - Status: {response.status_code}")
        assert response.status_code == 200
        assert response.json()["title"] == TEST_JOB["title"]
    
    @pytest.mark.asyncio
    async def test_create_job_as_admin(self, async_client, admin_token):
        """Test POST /api/jobs/ - Create job as admin."""
        job_data = {
            "title": "Admin Created Job",
            "description": "Job created by admin",
            "location": "NYC",
            "salary_range": "$200k+",
            "is_active": True,
            "recruiter_id": 1
        }
        
        response = await async_client.post(
            "/api/jobs/",
            json=job_data,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        log_result("/api/jobs/", "POST", "PASS" if response.status_code == 200 else "FAIL",
                  f"Create job as admin - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_create_job_as_seeker_unauthorized(self, async_client, seeker_data):
        """Test POST /api/jobs/ - Seeker cannot create jobs."""
        response = await async_client.post(
            "/api/jobs/",
            json=TEST_JOB,
            headers={
                "Authorization": f"Bearer {seeker_data['token']}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        expected = response.status_code == 403
        log_result("/api/jobs/", "POST", "PASS" if expected else "FAIL",
                  f"Seeker job creation rejection - Status: {response.status_code}")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_job_by_id(self, async_client):
        """Test GET /api/jobs/{job_id} - Get specific job."""
        # First get the list to find a valid ID
        list_response = await async_client.get("/api/jobs/")
        if list_response.status_code == 200 and len(list_response.json()) > 0:
            job_id = list_response.json()[0]["id"]
            response = await async_client.get(f"/api/jobs/{job_id}")
            log_result(f"/api/jobs/{job_id}", "GET", 
                      "PASS" if response.status_code == 200 else "FAIL",
                      f"Status: {response.status_code}")
            assert response.status_code == 200
        else:
            log_result("/api/jobs/{id}", "GET", "SKIP", "No jobs available")
    
    @pytest.mark.asyncio
    async def test_get_job_not_found(self, async_client):
        """Test GET /api/jobs/{job_id} - Job not found."""
        response = await async_client.get("/api/jobs/99999")
        expected = response.status_code == 404
        log_result("/api/jobs/99999", "GET", "PASS" if expected else "FAIL",
                  f"Job not found - Status: {response.status_code}")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_list_recruiter_jobs(self, async_client, recruiter_data):
        """Test GET /api/jobs/recruiter/{recruiter_id} - List recruiter's jobs."""
        recruiter_id = recruiter_data["user"]["id"]
        response = await async_client.get(
            f"/api/jobs/recruiter/{recruiter_id}",
            headers={"Authorization": f"Bearer {recruiter_data['token']}"}
        )
        log_result(f"/api/jobs/recruiter/{recruiter_id}", "GET",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Status: {response.status_code}")
        assert response.status_code == 200


# ============ APPLICATIONS API TESTS ============
class TestApplicationsAPI:
    """Test Applications API endpoints."""
    
    @pytest.mark.asyncio
    async def test_apply_to_job(self, async_client, seeker_data):
        """Test POST /api/applications/apply - Apply to a job."""
        # Get available jobs
        jobs_response = await async_client.get("/api/jobs/")
        if jobs_response.status_code != 200 or len(jobs_response.json()) == 0:
            log_result("/api/applications/apply", "POST", "SKIP", "No jobs available")
            return
        
        job_id = jobs_response.json()[0]["id"]
        seeker_id = seeker_data["user"]["id"]
        
        response = await async_client.post(
            "/api/applications/apply",
            data={"job_id": job_id, "seeker_id": seeker_id},
            headers={
                "Authorization": f"Bearer {seeker_data['token']}"
            }
        )
        log_result("/api/applications/apply", "POST",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Apply to job - Status: {response.status_code}")
        # May be 200 or 400 if already applied
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_list_my_applications(self, async_client, seeker_data):
        """Test GET /api/applications/me - List seeker's applications."""
        seeker_id = seeker_data["user"]["id"]
        response = await async_client.get(
            f"/api/applications/me?seeker_id={seeker_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        log_result("/api/applications/me", "GET",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"List my applications - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_list_job_applications_as_recruiter(self, async_client, admin_token):
        """Test GET /api/applications/job/{job_id} - Recruiter lists applications."""
        # Get available jobs
        jobs_response = await async_client.get("/api/jobs/")
        if jobs_response.status_code != 200 or len(jobs_response.json()) == 0:
            log_result("/api/applications/job/{id}", "GET", "SKIP", "No jobs available")
            return
        
        job_id = jobs_response.json()[0]["id"]
        response = await async_client.get(
            f"/api/applications/job/{job_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        log_result(f"/api/applications/job/{job_id}", "GET",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_update_application_status(self, async_client, admin_token, seeker_data):
        """Test PATCH /api/applications/{id}/status - Update application status."""
        seeker_id = seeker_data["user"]["id"]
        
        # Get seeker's applications
        apps_response = await async_client.get(
            f"/api/applications/me?seeker_id={seeker_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        
        if apps_response.status_code != 200 or len(apps_response.json()) == 0:
            log_result("/api/applications/{id}/status", "PATCH", "SKIP", "No applications available")
            return
        
        app_id = apps_response.json()[0]["id"]
        response = await async_client.patch(
            f"/api/applications/{app_id}/status",
            json={"status": "Interview Required"},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        log_result(f"/api/applications/{app_id}/status", "PATCH",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Update status - Status: {response.status_code}")
        assert response.status_code == 200


# ============ QUESTIONS API TESTS ============
class TestQuestionsAPI:
    """Test Questions API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_domains(self, async_client):
        """Test GET /api/questions/domains - List question domains."""
        response = await async_client.get("/api/questions/domains")
        log_result("/api/questions/domains", "GET",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Status: {response.status_code}, Domains: {response.json() if response.status_code == 200 else 'N/A'}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_questions_by_domain(self, async_client):
        """Test GET /api/questions/domain/{domain} - Get domain questions."""
        # Try common domains
        for domain in ["AI-ML", "Fullstack", "Cybersecurity"]:
            response = await async_client.get(f"/api/questions/domain/{domain}")
            log_result(f"/api/questions/domain/{domain}", "GET",
                      "PASS" if response.status_code == 200 else "WARN",
                      f"Status: {response.status_code}, Count: {len(response.json()) if response.status_code == 200 else 0}")
    
    @pytest.mark.asyncio
    async def test_get_job_questionnaire(self, async_client, seeker_data):
        """Test GET /api/questions/job/{job_id} - Get job questionnaire."""
        # Get available jobs
        jobs_response = await async_client.get("/api/jobs/")
        if jobs_response.status_code != 200 or len(jobs_response.json()) == 0:
            log_result("/api/questions/job/{id}", "GET", "SKIP", "No jobs available")
            return
        
        job_id = jobs_response.json()[0]["id"]
        response = await async_client.get(
            f"/api/questions/job/{job_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        # May return 404 if no questionnaire exists
        log_result(f"/api/questions/job/{job_id}", "GET",
                  "PASS" if response.status_code in [200, 404] else "FAIL",
                  f"Status: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_submit_text_answer(self, async_client, seeker_data):
        """Test POST /api/questions/answer/text - Submit text answer."""
        seeker_id = seeker_data["user"]["id"]
        
        # Get seeker's applications
        apps_response = await async_client.get(
            f"/api/applications/me?seeker_id={seeker_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        
        if apps_response.status_code != 200 or len(apps_response.json()) == 0:
            log_result("/api/questions/answer/text", "POST", "SKIP", "No applications available")
            return
        
        app_id = apps_response.json()[0]["id"]
        
        # Submit a test answer (question_id=1 may or may not exist)
        response = await async_client.post(
            "/api/questions/answer/text",
            json={
                "application_id": app_id,
                "question_id": 1,
                "answer_text": "Test answer submission"
            },
            headers={
                "Authorization": f"Bearer {seeker_data['token']}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        log_result("/api/questions/answer/text", "POST",
                  "PASS" if response.status_code in [200, 404] else "FAIL",
                  f"Submit answer - Status: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_get_application_answers(self, async_client, seeker_data):
        """Test GET /api/questions/answers/{application_id} - Get answers."""
        seeker_id = seeker_data["user"]["id"]
        
        # Get seeker's applications
        apps_response = await async_client.get(
            f"/api/applications/me?seeker_id={seeker_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        
        if apps_response.status_code != 200 or len(apps_response.json()) == 0:
            log_result("/api/questions/answers/{id}", "GET", "SKIP", "No applications available")
            return
        
        app_id = apps_response.json()[0]["id"]
        response = await async_client.get(
            f"/api/questions/answers/{app_id}",
            headers={"Authorization": f"Bearer {seeker_data['token']}"}
        )
        log_result(f"/api/questions/answers/{app_id}", "GET",
                  "PASS" if response.status_code == 200 else "FAIL",
                  f"Get answers - Status: {response.status_code}")
        assert response.status_code == 200


# ============ SESSION API TESTS ============
class TestSessionAPI:
    """Test Capture Session API endpoints."""
    
    @pytest.mark.asyncio
    async def test_session_start_requires_auth(self, async_client):
        """Test POST /api/session/start requires authentication."""
        response = await async_client.post(
            "/api/session/start",
            json={"candidate_id": "test123"},
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        expected = response.status_code == 401
        log_result("/api/session/start", "POST", "PASS" if expected else "FAIL",
                  f"Auth required - Status: {response.status_code}")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_session_stop_requires_auth(self, async_client):
        """Test POST /api/session/stop requires authentication."""
        response = await async_client.post(
            "/api/session/stop?candidate_id=test123",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        expected = response.status_code == 401
        log_result("/api/session/stop", "POST", "PASS" if expected else "FAIL",
                  f"Auth required - Status: {response.status_code}")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_session_heartbeat_requires_auth(self, async_client):
        """Test POST /api/session/heartbeat requires authentication."""
        response = await async_client.post(
            "/api/session/heartbeat?candidate_id=test123",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        expected = response.status_code == 401
        log_result("/api/session/heartbeat", "POST", "PASS" if expected else "FAIL",
                  f"Auth required - Status: {response.status_code}")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_session_summary_requires_auth(self, async_client):
        """Test GET /api/session/summary requires authentication."""
        response = await async_client.get("/api/session/summary?candidate_id=test123")
        expected = response.status_code == 401
        log_result("/api/session/summary", "GET", "PASS" if expected else "FAIL",
                  f"Auth required - Status: {response.status_code}")
        assert response.status_code == 401


# ============ STATIC PAGE TESTS ============
class TestStaticPages:
    """Test static HTML page routes."""
    
    @pytest.mark.asyncio
    async def test_root_page(self, async_client):
        """Test GET / - Root page."""
        response = await async_client.get("/")
        log_result("/", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Root page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_login_page(self, async_client):
        """Test GET /login - Login page."""
        response = await async_client.get("/login")
        log_result("/login", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Login page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_register_page(self, async_client):
        """Test GET /register - Register page."""
        response = await async_client.get("/register")
        log_result("/register", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Register page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_jobs_page(self, async_client):
        """Test GET /jobs - Jobs page."""
        response = await async_client.get("/jobs")
        log_result("/jobs", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Jobs page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_dashboard_page(self, async_client):
        """Test GET /dashboard - Dashboard page."""
        response = await async_client.get("/dashboard")
        log_result("/dashboard", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Dashboard page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_page(self, async_client):
        """Test GET /admin - Admin page."""
        response = await async_client.get("/admin")
        log_result("/admin", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Admin page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_interview_page(self, async_client):
        """Test GET /interview - Interview page."""
        response = await async_client.get("/interview")
        log_result("/interview", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Interview page - Status: {response.status_code}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_review_page(self, async_client):
        """Test GET /review - Review answers page."""
        response = await async_client.get("/review")
        log_result("/review", "GET", "PASS" if response.status_code == 200 else "FAIL",
                  f"Review page - Status: {response.status_code}")
        assert response.status_code == 200


# ============ SECURITY TESTS ============
class TestSecurityFeatures:
    """Test security features and access control."""
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, async_client):
        """Test CSRF protection for JSON POST without X-Requested-With header."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "csrf_test@test.com",
                "password": "TestPass123",
                "full_name": "CSRF Test",
                "role": "seeker"
            }
            # Missing X-Requested-With header
        )
        expected = response.status_code == 403
        log_result("/api/auth/register", "POST", "PASS" if expected else "FAIL",
                  f"CSRF protection - Status: {response.status_code}")
        # Note: CSRF is bypassed if Authorization header is present
    
    @pytest.mark.asyncio
    async def test_seeker_cannot_access_recruiter_endpoints(self, async_client, seeker_data):
        """Test role-based access control - Seeker cannot access recruiter endpoints."""
        # Try to create a job as seeker
        response = await async_client.post(
            "/api/jobs/",
            json={
                "title": "Unauthorized Job",
                "description": "Should not be allowed",
                "location": "Test",
                "recruiter_id": 1
            },
            headers={
                "Authorization": f"Bearer {seeker_data['token']}",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        expected = response.status_code == 403
        log_result("/api/jobs/ [RBAC]", "POST", "PASS" if expected else "FAIL",
                  f"Role-based access control - Status: {response.status_code}")
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, async_client):
        """Test that invalid JWT tokens are rejected."""
        response = await async_client.get(
            "/api/applications/me?seeker_id=1",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        expected = response.status_code == 401
        log_result("/api/applications/me [Invalid Token]", "GET", 
                  "PASS" if expected else "FAIL",
                  f"Invalid token rejection - Status: {response.status_code}")
        assert response.status_code == 401


# ============ GENERATE REPORT ============
def generate_test_report():
    """Generate a comprehensive test report."""
    report = []
    report.append("=" * 80)
    report.append("AI INTERVIEW SYSTEM - API TEST REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Tests Run: {len(TEST_RESULTS)}")
    
    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    skipped = sum(1 for r in TEST_RESULTS if r["status"] == "SKIP")
    warned = sum(1 for r in TEST_RESULTS if r["status"] == "WARN")
    
    report.append(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped} | Warnings: {warned}")
    report.append("\n" + "-" * 80)
    report.append("DETAILED RESULTS:")
    report.append("-" * 80)
    
    # Group by category
    categories = {}
    for result in TEST_RESULTS:
        endpoint = result["endpoint"]
        if "/auth" in endpoint:
            cat = "Authentication"
        elif "/jobs" in endpoint:
            cat = "Jobs"
        elif "/applications" in endpoint:
            cat = "Applications"
        elif "/questions" in endpoint:
            cat = "Questions"
        elif "/session" in endpoint:
            cat = "Session"
        elif result["endpoint"] in ["/", "/login", "/register", "/jobs", "/dashboard", "/admin", "/interview", "/review"]:
            cat = "Static Pages"
        else:
            cat = "Other"
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    for cat, results in categories.items():
        report.append(f"\n### {cat}")
        for r in results:
            status_icon = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️" if r["status"] == "WARN" else "⏭️"
            report.append(f"  {status_icon} [{r['method']}] {r['endpoint']} - {r['details']}")
    
    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING COMPREHENSIVE API END-TO-END TESTS")
    print("=" * 60 + "\n")
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure for debugging
        "--asyncio-mode=auto"
    ])
    
    # Generate and print report
    print("\n")
    print(generate_test_report())
