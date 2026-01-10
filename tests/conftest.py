import os
import pytest
from typing import Generator

# Set environment variables for testing
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["SECRET_KEY"] = "super_secret_testing_key"
os.environ["GEMINI_API_KEY"] = "fake_key_for_testing"
os.environ["JWT_ALGORITHM"] = "HS256"

# Mock external services
from unittest.mock import MagicMock
import sys

mock_genai = MagicMock()
mock_model = MagicMock()

def genai_side_effect(*args, **kwargs):
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
        m.text = "Generic response content."
        
    return m

mock_model.generate_content.side_effect = genai_side_effect
mock_model.generate_content_async.side_effect = genai_side_effect

mock_types = MagicMock()
mock_types.HarmCategory = MagicMock()
mock_types.HarmBlockThreshold = MagicMock()
mock_genai.types = mock_types

# Mock the new google.genai API
mock_genai.Client = MagicMock(return_value=mock_genai)
mock_genai.Client.return_value.models.generate_content = mock_model.generate_content
mock_genai.Client.return_value.aio = MagicMock()
mock_genai.Client.return_value.aio.models = MagicMock()
mock_genai.Client.return_value.aio.models.generate_content = mock_model.generate_content_async

sys.modules["google.genai"] = mock_genai
sys.modules["google.genai.types"] = mock_types

# Import app after setting env vars
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.adapters.database import get_db

@pytest.fixture(scope="session")
def engine():
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def session(engine) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

from app.core.security import verify_firebase_token

@pytest.fixture(scope="function")
def client(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session
        
    def mock_verify_firebase_token_override():
        return {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token_override
    
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

from unittest.mock import AsyncMock, patch

@pytest.fixture(scope="function", autouse=True)
def mock_gemini_adapter_fixture():
    # Return a valid JSON for parsing, but simple string for others?
    # This acts as a catch-all response for generate_text
    response_text = '{"name": "Test User", "email": "test@example.com", "skills": ["Python"], "projects": [], "experience": [], "education": []}'
    
    with patch("app.adapters.gemini_adapter.gemini_adapter.generate_text", new_callable=AsyncMock) as mock_freq:
        mock_freq.return_value = response_text
        with patch("app.adapters.gemini_adapter.gemini_adapter.vision_to_text", new_callable=AsyncMock) as mock_vision:
            mock_vision.return_value = "Raw Text"
            yield

