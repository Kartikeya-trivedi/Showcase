
"""
WebSocket endpoint for real-time chat with AI assistant.
This module maintains backward compatibility with existing chatbot frontend
while integrating with production backend (GeminiAdapter, ChatService, database).
Protocol (unchanged for frontend):
- Client connects to: ws://host/chat/ws
- Client sends: Plain text messages
- Server sends: Streamed text chunks + "__END_OF_STREAM__" marker
"""
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.adapters.database import get_db
from app.adapters.gemini_adapter import GeminiAdapter, GeminiError
from app.services.chat_services import ChatService

logger = logging.getLogger(__name__)
router = APIRouter()
# Global Gemini adapter (initialized in main.py)
gemini_adapter: Optional[GeminiAdapter] = None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time chat WebSocket endpoint.
    
    IMPORTANT: This endpoint maintains exact compatibility with existing
    chatbot frontend. Do not change the protocol without coordinating
    with the chatbot team.
    
    Protocol:
        - Client sends: Plain text messages
        - Server sends: Streamed text chunks
        - Stream end marker: "__END_OF_STREAM__"
    """
    
    await websocket.accept()
    logger.info("WebSocket Connected - Using Gemini Next-Gen")
    
    # Session management
    user_id = "dev_user_01"  # Placeholder until auth is implemented
    session_id = str(uuid.uuid4())
    
    # Get database session
    db_gen = get_db()
    db: AsyncSession = await anext(db_gen)
    
    try:
        # Main chat loop
        while True:
            # Receive user message
            user_input = await websocket.receive_text()
            
            if not user_input.strip():
                continue
            
            logger.info(f"User message received (session: {session_id})")
            
            # Save user message to database
            try:
                await ChatService.save_message(
                    db=db,
                    user_id=user_id,
                    session_id=session_id,
                    role="user",
                    content=user_input,
                )
            except Exception as e:
                logger.error(f"❌ Failed to save user message: {e}")
                # Continue anyway - don't break chat for DB errors
            
            # Get AI response using production GeminiAdapter
            full_response_text = ""
            
            try:
                # Call Gemini via your production adapter
                response_text = await gemini_adapter.generate_text(
                    prompt=user_input,
                    temperature=0.7,
                    max_tokens=2048,
                )
                
                # Stream response in chunks (mimics SDK streaming behavior)
                # This maintains the same user experience as before
                chunk_size = 20  # Characters per chunk
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i:i + chunk_size]
                    if chunk:
                        await websocket.send_text(chunk)
                        full_response_text += chunk
                
            except GeminiError as e:
                # Handle Gemini-specific errors gracefully
                logger.error(f"Gemini Error: {str(e)}")
                error_message = f"Error: {str(e)}"
                await websocket.send_text(error_message)
                full_response_text = error_message
            
            except Exception as e:
                # Catch-all for unexpected errors
                logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
                error_message = f"Error: {str(e)}"
                await websocket.send_text(error_message)
                full_response_text = error_message
            
            # Send end-of-stream marker (required by frontend)
            await websocket.send_text("__END_OF_STREAM__")
            
            # Save assistant response to database
            if full_response_text.strip():
                try:
                    await ChatService.save_message(
                        db=db,
                        user_id=user_id,
                        session_id=session_id,
                        role="assistant",
                        content=full_response_text,
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to save assistant message: {e}")
                    # Continue anyway - don't break chat for DB errors
    
    except WebSocketDisconnect:
        logger.info("Connection closed")
    
    except Exception as e:
        logger.error(f"WebSocket Error: {str(e)}", exc_info=True)
        try:
            await websocket.send_text(f"Error: {str(e)}")
        except:
            pass  # Connection might already be closed
    
    finally:
        # Clean up database session
        try:
            await db_gen.aclose()
        except Exception as e:
            logger.error(f"Failed to close DB session: {e}")
