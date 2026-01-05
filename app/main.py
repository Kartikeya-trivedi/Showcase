"""
FastAPI main application entry point with Real-Time WebSockets.
"""
import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.database import engine, Base
from app.api.routes import router

load_dotenv()

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        # Keeps track of active "open phone lines"
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()
# --------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Resume Processing Pipeline API",
    description="API for processing resumes through OCR, AI, and frontend generation",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Standard API Routes
app.include_router(router, prefix="/api/v1")

# 2. REAL-TIME CHAT WEBSOCKET
@app.websocket("/ws/chat/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: int):
    """
    Real-time chat endpoint for a specific resume job.
    Matches the ChatMessage model's job_id requirement.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive text from the Lovable-style UI
            data = await websocket.receive_text()
            
            # TODO: Integrate with app.ai_pipeline to get actual Gemini response
            # For now, we echo back to confirm the "Real-Time" link is live
            response = f"AI Insight for Job {job_id}: I've analyzed your data. Query received: {data}"
            
            await manager.send_personal_message(response, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Static files setup
preview_dir = os.path.join(os.path.dirname(__file__), "..", "previews")
os.makedirs(preview_dir, exist_ok=True)
if os.path.exists(preview_dir):
    app.mount("/preview", StaticFiles(directory=preview_dir, html=True), name="preview")

@app.get("/")
async def root():
    return {"message": "Resume Processing Pipeline API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}