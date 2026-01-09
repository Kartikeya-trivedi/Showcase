
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

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Startup:
    - Create database tables (DEV MODE)
    - Initialize Gemini adapter for chat
    Shutdown:
    - Close Gemini adapter
    - Dispose database engine
    """
    
    logger.info("🚀 Showcase AI: Application starting up")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")
    
    # Initialize Gemini adapter for chat
    chat.gemini_adapter = GeminiAdapter(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.GEMINI_AGENT_MODEL,
        timeout_seconds=60,
        max_retries=3,
    )
    logger.info("✅ Gemini adapter initialized")
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("🛑 Showcase AI: Application shutting down")
    
    # Close Gemini adapter
    if chat.gemini_adapter:
        await chat.gemini_adapter.close()
        logger.info("Gemini adapter closed")
    
    # Dispose database engine
    await engine.dispose()
    logger.info("Database engine disposed")

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
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
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
