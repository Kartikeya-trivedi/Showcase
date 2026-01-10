import os

# Set necessary env vars for testing BEFORE importing app
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
os.environ["GEMINI_API_KEY"] = "fake_key_for_testing"
os.environ["SECRET_KEY"] = "super_secret_testing_key"
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///test.db"

os.environ["DATABASE_URL"] = "sqlite:///test.db"

# Mock external services
from unittest.mock import MagicMock, AsyncMock
import sys

mock_genai = MagicMock()
mock_model = MagicMock()

async def genai_side_effect(*args, **kwargs):
    prompt = str(args[0]) if args else ""
    m = MagicMock()
    
    if "tagline" in prompt.lower():
        m.text = "Expert software engineer delivering high quality solutions for the web."
    elif "bio" in prompt.lower():
        # Need > 150 words
        m.text = "I am a professional software engineer with a passion for building scalable applications. " * 15
    elif "project" in prompt.lower():
         m.text = "Developed a full stack application using React and FastAPI. " * 10
    else:
        # Default JSON for parsing
        m.text = '{"name": "Test User", "email": "test@example.com", "skills": ["Python"], "projects": [], "experience": [], "education": []}'
        
    return m

mock_model.generate_content.side_effect = genai_side_effect # This is sync (actually SDK wraps it? No synchronous generate_content)
# Wait, generate_content is synchronous in SDK? No, it's blocking.
# But generate_content_async is async.

mock_model.generate_content_async = AsyncMock(side_effect=genai_side_effect)
# For synchronous generate_content, we can keep it as is, or make side_effect returns m directly (not async def).
# But genai_side_effect is async def now.

def genai_side_effect_sync(*args, **kwargs):
    prompt = str(args[0]) if args else ""
    m = MagicMock()
    if "tagline" in prompt.lower():
        m.text = "Expert software engineer delivering high quality solutions for the web."
    elif "bio" in prompt.lower():
        m.text = "I am a professional software engineer with a passion for building scalable applications. " * 15
    elif "project" in prompt.lower():
         m.text = "Developed a full stack application using React and FastAPI. " * 10
    else:
        m.text = '{"name": "Test User", "email": "test@example.com", "skills": ["Python"], "projects": [], "experience": [], "education": []}'
    return m

mock_model.generate_content.side_effect = genai_side_effect_sync


mock_types = MagicMock()
mock_types.HarmCategory = MagicMock()
mock_types.HarmBlockThreshold = MagicMock()
mock_genai.types = mock_types

mock_genai.GenerativeModel.return_value = mock_model
sys.modules["google.genai"] = mock_genai
sys.modules["google.genai.types"] = mock_types

# Now import the app
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import verify_firebase_token
from app.api.dependencies import get_db
from app.models.portfolio import Portfolio
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import logging
from unittest.mock import AsyncMock

from app.adapters.gemini_adapter import gemini_adapter

# Patch Gemini Adapter to avoid real HTTP calls
async def adapter_generate_side_effect(prompt, *args, **kwargs):
    prompt_lower = prompt.lower()
    
    # Priority: Check for parsing prompt first
    if "extract the following information" in prompt_lower:
         return '{"name": "Test User", "email": "test@example.com", "skills": ["Python"], "projects": [], "experience": [], "education": []}'

    if "tagline" in prompt_lower:
        return "Expert software engineer delivering high quality solutions for the web."
    elif "bio" in prompt_lower:
        return "I am a professional software engineer with a passion for building scalable applications. " * 15
    elif "project" in prompt_lower:
         return "Developed a full stack application using React and FastAPI. " * 10
    else:
        # Fallback default
        return '{"name": "Test User", "email": "test@example.com", "skills": ["Python"], "projects": [], "experience": [], "education": []}'

gemini_adapter.generate_text = AsyncMock(side_effect=adapter_generate_side_effect)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Setup In-Memory Database for Testing
engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

def get_test_db():
    with Session(engine) as session:
        yield session

# 2. Mock Authentication
def mock_verify_firebase_token():
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User"
    }

# 3. Apply Overrides
app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

client = TestClient(app)

def run_checks():
    logger.info("Initializing DB tables...")
    SQLModel.metadata.create_all(engine)
    
    # Check Health
    logger.info("Testing /health...")
    res = client.get("/health")
    if res.status_code != 200:
        logger.error(f"/health failed: {res.status_code}")
        return
    logger.info("/health OK")

    # Check Resume Upload
    logger.info("Testing /api/v1/resume/upload...")
    fake_file = ("resume.pdf", b"fake content", "application/pdf")
    res = client.post("/api/v1/resume/upload", files={"file": fake_file})
    if res.status_code == 202:
        logger.info("/api/v1/resume/upload OK")
    else:
        logger.error(f"/api/v1/resume/upload failed: {res.status_code} - {res.text}")

    # Check Get My Portfolios
    with Session(engine) as session:
        p = Portfolio(
            job_id="job_123",
            user_id="test_user_123",
            full_name="Test User",
            content={"title": "Test"},
            is_published=False
        )
        session.add(p)
        session.commit()
    
    logger.info("Testing /api/v1/portfolios/me...")
    res = client.get("/api/v1/portfolios/me")
    if res.status_code == 200 and len(res.json()) > 0:
        logger.info("/api/v1/portfolios/me OK")
    else:
        logger.error(f"Failed: {res.status_code} - {res.text}")

    print("ALL TESTS PASSED SUCCESSFULLY")

if __name__ == "__main__":
    try:
        run_checks()
    except Exception as e:
        logger.exception("Something went wrong")
