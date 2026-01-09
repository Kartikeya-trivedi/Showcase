import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from app.schemas.resume import ResumeUploadResponse
from app.tasks import process_resume_task
from app.api import dependencies
from app.core.security import verify_firebase_token  # 🛡️ New Security Import

router = APIRouter()

@router.post("/upload", response_model=ResumeUploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db=Depends(dependencies.get_db),
    # Allow guest uploads for public demo
    # current_user: dict = Depends(verify_firebase_token) 
):
    # Mock user for public demo or extract from token manually if present
    current_user = {"uid": "guest_" + str(uuid.uuid4())[:8], "email": "guest@showcase.ai"}

    if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Please upload a PDF or an Image."
        )
    
    job_id = str(uuid.uuid4())

    user_id = current_user.get("uid")

    background_tasks.add_task(process_resume_task, job_id, file, user_id)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"Resume received for {current_user.get('email')}. Portfolio design in progress."
    }
