"""
Test script to upload a resume via the API and check the results.
This tests the full pipeline including PyMuPDF extraction.
"""
import sys
import requests
import time
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_upload_resume(pdf_path: str):
    """Test uploading a resume and checking the job status."""
    
    if not Path(pdf_path).exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return None
    
    print("=" * 70)
    print("API Upload Test")
    print("=" * 70)
    print(f"\n[INFO] Uploading: {pdf_path}")
    
    # Upload file
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(
                f"{API_BASE_URL}/resume/upload",
                files=files,
                timeout=30
            )
        
        if response.status_code != 202:
            print(f"[ERROR] Upload failed: {response.status_code}")
            print(f"         Response: {response.text}")
            return None
        
        data = response.json()
        job_id = data.get('job_id')
        
        if not job_id:
            print(f"[ERROR] No job_id in response: {data}")
            return None
        
        print(f"[OK] Upload successful!")
        print(f"     Job ID: {job_id}")
        print(f"     Status: {data.get('status')}")
        
        return job_id
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server")
        print("        Make sure the server is running: uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_job_status(job_id: str, max_wait: int = 120):
    """Check job status and wait for completion."""
    
    print(f"\n[INFO] Checking job status...")
    print(f"       Job ID: {job_id}")
    print(f"       Max wait: {max_wait} seconds")
    
    start_time = time.time()
    last_status = None
    
    while True:
        try:
            response = requests.get(
                f"{API_BASE_URL}/jobs/{job_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"[ERROR] Status check failed: {response.status_code}")
                print(f"         Response: {response.text}")
                break
            
            data = response.json()
            status = data.get('status')
            progress = data.get('progress_percentage', 0)
            stage = data.get('current_stage', 'unknown')
            
            # Only print if status changed
            if status != last_status:
                print(f"\n[STATUS] {status.upper()}")
                print(f"         Progress: {progress}%")
                print(f"         Stage: {stage}")
                last_status = status
            
            # Check if completed
            if status == 'completed':
                elapsed = time.time() - start_time
                print(f"\n[SUCCESS] Job completed in {elapsed:.1f} seconds!")
                print(f"         Portfolio ID: {data.get('portfolio_id')}")
                return True
            
            # Check if failed
            if status == 'failed':
                print(f"\n[FAILED] Job failed!")
                error = data.get('error', {})
                print(f"         Error: {error.get('message', 'Unknown error')}")
                print(f"         Stage: {error.get('stage', 'unknown')}")
                return False
            
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                print(f"\n[TIMEOUT] Job did not complete within {max_wait} seconds")
                return False
            
            # Wait before next check
            time.sleep(2)
            
        except requests.exceptions.ConnectionError:
            print("[ERROR] Lost connection to server")
            return False
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user")
            return False
        except Exception as e:
            print(f"[ERROR] Status check error: {e}")
            time.sleep(2)

def get_portfolio(job_id: str):
    """Get the generated portfolio."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/portfolio/{job_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            portfolio = response.json()
            print(f"\n[OK] Portfolio retrieved!")
            print(f"     Name: {portfolio.get('full_name')}")
            print(f"     Slug: {portfolio.get('slug')}")
            print(f"     Has content: {bool(portfolio.get('content'))}")
            
            if portfolio.get('content'):
                content = portfolio['content']
                print(f"     Content keys: {list(content.keys())}")
                if 'hero' in content:
                    print(f"     Hero name: {content['hero'].get('name', 'N/A')}")
                if 'projects' in content:
                    print(f"     Projects: {len(content['projects'])}")
                if 'skills' in content:
                    print(f"     Skills categories: {len(content['skills'])}")
            
            return portfolio
        else:
            print(f"[ERROR] Could not get portfolio: {response.status_code}")
            print(f"         Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Portfolio retrieval failed: {e}")
        return None

def main():
    """Run the full API test."""
    
    # Get PDF file path
    pdf_path = input("Enter path to PDF resume file: ").strip()
    
    # Clean up path: remove quotes and normalize
    pdf_path = pdf_path.strip('"').strip("'")
    pdf_path = os.path.normpath(pdf_path)
    
    if not pdf_path:
        print("[ERROR] No file path provided")
        return
    
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        print(f"        Current directory: {os.getcwd()}")
        return
    
    # Test 1: Upload
    job_id = test_upload_resume(pdf_path)
    if not job_id:
        return
    
    # Test 2: Check status
    success = check_job_status(job_id)
    
    if success:
        # Test 3: Get portfolio
        print("\n" + "=" * 70)
        print("Retrieving Portfolio")
        print("=" * 70)
        portfolio = get_portfolio(job_id)
        
        if portfolio:
            print("\n[SUCCESS] Full pipeline test completed!")
        else:
            print("\n[WARNING] Pipeline completed but portfolio not found")
    else:
        print("\n[FAILED] Pipeline test failed")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOP] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
