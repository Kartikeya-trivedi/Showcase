"""
Quick diagnostic script to check job and portfolio status.
Usage: python check_job.py <job_id>
"""
import sys
import os
from sqlmodel import Session, select
from app.adapters.database import engine
from app.models.job import Job
from app.models.portfolio import Portfolio

def check_job(job_id: str):
    """Check job and portfolio status for a given job_id."""
    print(f"\n{'='*60}")
    print(f"Diagnostic Check for Job ID: {job_id}")
    print(f"{'='*60}\n")
    
    with Session(engine) as db:
        # Check job
        job_statement = select(Job).where(Job.job_id == job_id)
        job = db.exec(job_statement).first()
        
        if not job:
            print("[X] JOB NOT FOUND")
            print(f"   No job record found with job_id: {job_id}")
            print("\n   Possible reasons:")
            print("   - Job ID is incorrect")
            print("   - Job was never created")
            print("   - Database connection issue")
            return
        
        print("[OK] JOB FOUND")
        print(f"   Status: {job.status.value if job.status else 'None'}")
        print(f"   Progress: {job.progress_percentage}%")
        print(f"   Current Stage: {job.current_stage or 'N/A'}")
        print(f"   User ID: {job.user_id}")
        print(f"   Created: {job.created_at}")
        print(f"   Started: {job.started_at or 'Not started'}")
        print(f"   Completed: {job.completed_at or 'Not completed'}")
        print(f"   Duration: {job.duration_seconds or 'N/A'} seconds")
        print(f"   Portfolio ID: {job.portfolio_id or 'None'}")
        
        if job.error_message:
            print(f"\n   [!] ERROR DETECTED:")
            print(f"   Error Message: {job.error_message}")
            if job.error_details:
                print(f"   Error Details: {job.error_details}")
            print(f"   Failed at stage: {job.current_stage or 'Unknown'}")
        
        # Check portfolio
        portfolio_statement = select(Portfolio).where(Portfolio.job_id == job_id)
        portfolio = db.exec(portfolio_statement).first()
        
        print(f"\n{'='*60}")
        if portfolio:
            print("[OK] PORTFOLIO FOUND")
            print(f"   Portfolio ID: {portfolio.id}")
            print(f"   Full Name: {portfolio.full_name}")
            print(f"   Slug: {portfolio.slug}")
            print(f"   Has Content: {bool(portfolio.content)}")
            if isinstance(portfolio.content, dict):
                print(f"   Content Keys: {list(portfolio.content.keys())}")
                print(f"   Hero Name: {portfolio.content.get('hero', {}).get('name', 'N/A')}")
                print(f"   Projects: {len(portfolio.content.get('projects', []))}")
                print(f"   Skills: {len(portfolio.content.get('skills', []))}")
            print(f"   Created: {portfolio.created_at}")
        else:
            print("[X] PORTFOLIO NOT FOUND")
            print(f"   No portfolio record found for job_id: {job_id}")
            
            if job.status.value == "completed":
                print("\n   [!] ISSUE DETECTED:")
                print("   Job is marked as COMPLETED but portfolio doesn't exist!")
                print("   This indicates a problem during portfolio creation.")
                if job.portfolio_id:
                    print(f"   Job has portfolio_id ({job.portfolio_id}) but portfolio record missing.")
                    print("   Possible causes:")
                    print("   - Portfolio creation failed after job completion")
                    print("   - Database transaction rollback")
                    print("   - Portfolio was deleted")
            elif job.status.value == "failed":
                print("\n   [i] EXPECTED:")
                print("   Job failed before portfolio creation.")
                print(f"   Error: {job.error_message}")
            else:
                print("\n   [i] STATUS:")
                print(f"   Job is still {job.status.value} - portfolio will be created when job completes.")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_job.py <job_id>")
        print("\nExample:")
        print("  python check_job.py b0b361eb-484f-49bd-bb52-8a40fde12d00")
        sys.exit(1)
    
    job_id = sys.argv[1]
    check_job(job_id)
