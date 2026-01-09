
"""
FastAPI application entry point.
This module:
- Configures the FastAPI application
- Sets up CORS middleware
- Manages application lifespan (DB, adapters)
- Registers API routers
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import chat
from app.adapters.gemini_adapter import GeminiAdapter
from app.api.routes import api_router
from app.core.config import settings
from app.adapters.database import engine, Base
from app.models.portfolio import Portfolio
from app.models.chat_message import ChatMessage 
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.models.user import User  # GitHub OAuth user model

# --- YOUR SOUL INJECTION START ---
from app.chat import router as chat_router 
# --- YOUR SOUL INJECTION END ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """
    logger.info("Showcase AI: Application starting up")
    
    # Create tables
    # Note: In production you would use Alembic for migrations
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    yield
    
    logger.info("Showcase AI: Application shutting down")
    engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Showcase AI: Transforming resumes into stunning portfolios.",
    debug=settings.DEBUG,
    lifespan=lifespan,
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Allow all origins for development
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "engine": "Gemini-Vision-v1",
        "version": "1.0.0",
    }
