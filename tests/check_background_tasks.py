"""
Check if background tasks are actually running.
This helps diagnose why jobs are stuck.
"""
import sys
import asyncio
from sqlmodel import Session, select
from app.adapters.database import engine
from app.models.job import Job, JobStatus
from datetime import datetime, timedelta

def check_stuck_jobs():
    """Check for jobs that have been stuck for too long."""
    print("=" * 70)
    print("BACKGROUND TASK DIAGNOSTICS")
    print("=" * 70)
    
    with Session(engine) as db:
        # Get all jobs
        jobs = db.exec(select(Job)).all()
        
        now = datetime.utcnow()
        stuck_threshold = timedelta(minutes=5)  # Jobs stuck for more than 5 minutes
        
        print(f"\nTotal Jobs: {len(jobs)}")
        
        # Check pending jobs
        pending_jobs = [j for j in jobs if j.status == JobStatus.PENDING]
        print(f"\n[1] PENDING JOBS (Not Started): {len(pending_jobs)}")
        if pending_jobs:
            print("   These jobs were created but background tasks never started:")
            for job in pending_jobs:
                age = now - job.created_at if job.created_at else timedelta(0)
                print(f"   - Job {job.job_id[:8]}...")
                print(f"     Created: {job.created_at}")
                print(f"     Age: {age.total_seconds() / 60:.1f} minutes")
                print(f"     Filename: {job.original_filename}")
                if age > stuck_threshold:
                    print(f"     [!] STUCK - Should have started by now!")
                print()
        
        # Check processing jobs
        processing_jobs = [
            j for j in jobs 
            if j.status in [JobStatus.PROCESSING, JobStatus.OCR_EXTRACTING, 
                           JobStatus.AI_GENERATING, JobStatus.VALIDATING]
        ]
        print(f"\n[2] PROCESSING JOBS (Started but not completed): {len(processing_jobs)}")
        if processing_jobs:
            print("   These jobs started but haven't completed:")
            for job in processing_jobs:
                age = (now - job.started_at).total_seconds() / 60 if job.started_at else 0
                print(f"   - Job {job.job_id[:8]}...")
                print(f"     Status: {job.status.value}")
                print(f"     Progress: {job.progress_percentage}%")
                print(f"     Stage: {job.current_stage}")
                print(f"     Started: {job.started_at}")
                print(f"     Running for: {age:.1f} minutes")
                if age > 10:  # More than 10 minutes is suspicious
                    print(f"     [!] STUCK - Processing for too long!")
                print()
        
        # Check failed jobs
        failed_jobs = [j for j in jobs if j.status == JobStatus.FAILED]
        print(f"\n[3] FAILED JOBS: {len(failed_jobs)}")
        if failed_jobs:
            print("   Recent failures:")
            for job in failed_jobs[-5:]:
                print(f"   - Job {job.job_id[:8]}...")
                print(f"     Error: {job.error_message}")
                print(f"     Stage: {job.current_stage}")
                print(f"     Failed at: {job.completed_at}")
                print()
        
        # Check completed jobs
        completed_jobs = [j for j in jobs if j.status == JobStatus.COMPLETED]
        print(f"\n[4] COMPLETED JOBS: {len(completed_jobs)}")
        if completed_jobs:
            print("   Successful completions:")
            for job in completed_jobs[-5:]:
                print(f"   - Job {job.job_id[:8]}...")
                print(f"     Duration: {job.duration_seconds:.1f}s")
                print(f"     Has Portfolio: {bool(job.portfolio_id)}")
                print()
        else:
            print("   [!] NO JOBS HAVE COMPLETED SUCCESSFULLY!")
        
        # Recommendations
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        
        if len(pending_jobs) > 0:
            print("\n[!] Pending jobs detected:")
            print("   - FastAPI BackgroundTasks may not be running")
            print("   - Check server logs for errors")
            print("   - Verify background_tasks.add_task() is working")
            print("   - Consider using Celery or a proper task queue")
        
        if len(processing_jobs) > 0:
            print("\n[!] Stuck processing jobs detected:")
            print("   - Jobs started but aren't completing")
            print("   - Check OCR service logs")
            print("   - Verify Gemini API is working")
            print("   - Check for timeout issues")
        
        if len(completed_jobs) == 0:
            print("\n[!] CRITICAL: No jobs have completed!")
            print("   - Background tasks may not be executing")
            print("   - Check if FastAPI BackgroundTasks are working")
            print("   - Verify database connections")
            print("   - Check application logs for errors")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        check_stuck_jobs()
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
