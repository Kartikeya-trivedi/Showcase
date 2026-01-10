"""
Script to check what's stored in the database.
Run with: python check_database.py
"""
import sys
import os
from sqlmodel import Session, select
from app.adapters.database import engine
from app.models.job import Job
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.chat_message import ChatMessage

def check_database():
    """Check all data stored in the database."""
    print("=" * 70)
    print("DATABASE CONTENTS CHECK")
    print("=" * 70)
    
    with Session(engine) as db:
        # Check Jobs
        print("\n[1] JOBS TABLE")
        print("-" * 70)
        jobs = db.exec(select(Job)).all()
        print(f"Total Jobs: {len(jobs)}")
        
        if jobs:
            print("\nRecent Jobs:")
            for job in jobs[-10:]:  # Last 10 jobs
                print(f"  - Job ID: {job.job_id}")
                print(f"    Status: {job.status.value}")
                print(f"    Progress: {job.progress_percentage}%")
                print(f"    Stage: {job.current_stage}")
                print(f"    User: {job.user_id}")
                print(f"    Filename: {job.original_filename}")
                print(f"    Created: {job.created_at}")
                print(f"    Has Portfolio: {bool(job.portfolio_id)}")
                if job.portfolio_id:
                    print(f"    Portfolio ID: {job.portfolio_id}")
                if job.status.value == "failed":
                    print(f"    Error: {job.error_message}")
                print()
        else:
            print("  No jobs found in database.")
        
        # Check Portfolios
        print("\n[2] PORTFOLIOS TABLE")
        print("-" * 70)
        portfolios = db.exec(select(Portfolio)).all()
        print(f"Total Portfolios: {len(portfolios)}")
        
        if portfolios:
            print("\nRecent Portfolios:")
            for portfolio in portfolios[-10:]:  # Last 10 portfolios
                print(f"  - Portfolio ID: {portfolio.id}")
                print(f"    Job ID: {portfolio.job_id}")
                print(f"    Name: {portfolio.full_name}")
                print(f"    Slug: {portfolio.slug}")
                print(f"    User: {portfolio.user_id}")
                print(f"    Has Content: {bool(portfolio.content)}")
                if isinstance(portfolio.content, dict):
                    print(f"    Content Keys: {list(portfolio.content.keys())}")
                    if portfolio.content.get('hero'):
                        print(f"    Hero Name: {portfolio.content['hero'].get('name', 'N/A')}")
                    print(f"    Projects: {len(portfolio.content.get('projects', []))}")
                    print(f"    Skills: {len(portfolio.content.get('skills', []))}")
                print(f"    Created: {portfolio.created_at}")
                print(f"    Published: {portfolio.is_published}")
                print()
        else:
            print("  No portfolios found in database.")
        
        # Check Users
        print("\n[3] USERS TABLE")
        print("-" * 70)
        users = db.exec(select(User)).all()
        print(f"Total Users: {len(users)}")
        if users:
            for user in users[-5:]:  # Last 5 users
                print(f"  - User ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    Created: {user.created_at}")
                print()
        else:
            print("  No users found in database.")
        
        # Check Chat Messages (if table exists)
        print("\n[4] CHAT MESSAGES TABLE")
        print("-" * 70)
        try:
            messages = db.exec(select(ChatMessage)).all()
            print(f"Total Messages: {len(messages)}")
            if messages:
                print(f"  Last 5 messages:")
                for msg in messages[-5:]:
                    print(f"    - {msg.role}: {msg.content[:50]}...")
            else:
                print("  No messages found in database.")
        except Exception as e:
            print(f"  Table doesn't exist or error: {e}")
            messages = []
        
        # Summary Statistics
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)
        print(f"Total Jobs: {len(jobs)}")
        print(f"  - Completed: {sum(1 for j in jobs if j.status.value == 'completed')}")
        print(f"  - Failed: {sum(1 for j in jobs if j.status.value == 'failed')}")
        print(f"  - Processing: {sum(1 for j in jobs if j.status.value in ['processing', 'ocr_extracting', 'ai_generating', 'validating'])}")
        print(f"  - Pending: {sum(1 for j in jobs if j.status.value == 'pending')}")
        print(f"\nTotal Portfolios: {len(portfolios)}")
        print(f"  - Published: {sum(1 for p in portfolios if p.is_published)}")
        print(f"  - With Content: {sum(1 for p in portfolios if p.content)}")
        print(f"\nTotal Users: {len(users)}")
        print(f"Total Messages: {len(messages)}")
        
        # Check for orphaned records
        print("\n" + "=" * 70)
        print("DATA INTEGRITY CHECK")
        print("=" * 70)
        
        # Jobs without portfolios (but completed)
        completed_without_portfolio = [
            j for j in jobs 
            if j.status.value == "completed" and not j.portfolio_id
        ]
        if completed_without_portfolio:
            print(f"\n[!] WARNING: {len(completed_without_portfolio)} completed job(s) without portfolio:")
            for j in completed_without_portfolio:
                print(f"    - Job {j.job_id} (completed at {j.completed_at})")
        else:
            print("\n[OK] All completed jobs have portfolios.")
        
        # Portfolios without jobs (shouldn't happen)
        portfolios_without_job = []
        for p in portfolios:
            job = db.exec(select(Job).where(Job.job_id == p.job_id)).first()
            if not job:
                portfolios_without_job.append(p)
        
        if portfolios_without_job:
            print(f"\n[!] WARNING: {len(portfolios_without_job)} portfolio(s) without matching job:")
            for p in portfolios_without_job:
                print(f"    - Portfolio {p.id} (job_id: {p.job_id})")
        else:
            print("\n[OK] All portfolios have matching jobs.")
        
        # Jobs with portfolio_id but portfolio doesn't exist
        orphaned_portfolio_refs = []
        for j in jobs:
            if j.portfolio_id:
                portfolio = db.exec(select(Portfolio).where(Portfolio.id == j.portfolio_id)).first()
                if not portfolio:
                    orphaned_portfolio_refs.append(j)
        
        if orphaned_portfolio_refs:
            print(f"\n[!] WARNING: {len(orphaned_portfolio_refs)} job(s) with portfolio_id but portfolio missing:")
            for j in orphaned_portfolio_refs:
                print(f"    - Job {j.job_id} (portfolio_id: {j.portfolio_id})")
        else:
            print("\n[OK] All job portfolio references are valid.")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        check_database()
    except Exception as e:
        print(f"\n[X] Error checking database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
