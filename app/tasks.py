import logging
import time
from fastapi import UploadFile
from sqlmodel import Session
from app.adapters.database import engine
from app.models.portfolio import Portfolio
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

async def process_resume_task(job_id: str, file: UploadFile, user_id: str):
    start_time = time.time()
    logger.info(f"Job {job_id}: Processing started for User {user_id}")

    try:
        # Perform Async operations BEFORE opening the sync DB session
        # This keeps the blocking DB section as short as possible
        raw_text = await ocr_service.extract_text(file)
        
        if not raw_text or not raw_text.strip():
            raise ValueError(f"OCR returned empty content for Job {job_id}")
        
        portfolio_json = await ai_service.generate_portfolio_content(raw_text)
        logger.info(f"Job {job_id}: AI generation complete. Saving to DB...")

        # Now open Sync DB session for saving
        with Session(engine) as db:
            new_portfolio = Portfolio(
                job_id=job_id,
                user_id=user_id,
                full_name=portfolio_json.get("hero", {}).get("name", "Aspiring Professional"),
                content=portfolio_json,
                is_published=False
            )
            
            db.add(new_portfolio)
            db.commit()
            db.refresh(new_portfolio)
            
        duration = time.time() - start_time
        logger.info(f"Job {job_id}: Successfully completed in {duration:.2f}s")

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Job {job_id}: FAILED after {elapsed:.2f}s"
        logger.error(error_msg, exc_info=True)
        print(f"\n[BACKGROUND TASK ERROR] {error_msg}")
        print(e)  # Print exception directly to stdout for visibility
        # We can't easily rollback the specific session here if it closed, 
        # but the transaction context manager usually handles rollback on error.
        # Since we moved logic out, we just log.
        pass

    finally:
        await file.close()
        logger.debug(f"Resource cleanup for Job {job_id} finalized")
