
import asyncio
import sys
import os
import httpx

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.core.config import settings

async def test_gemini_basic():
    print("=" * 50)
    print("GEMINI BASIC CONNECTION TEST")
    print("=" * 50)
    
    # Check API key
    if not settings.GEMINI_API_KEY:
        print("\n[ERROR] GEMINI_API_KEY not found in .env file!")
        return 
    
    key_masked = f"{settings.GEMINI_API_KEY[:8]}...{settings.GEMINI_API_KEY[-4:]}"
    print(f"\nAPI Key: {key_masked}")
    
    params = {"key": settings.GEMINI_API_KEY}
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: List available models
        print("\n[Step 1] Fetching available models...")
        list_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        try:
            list_resp = await client.get(list_url, params=params)
            
            if list_resp.status_code != 200:
                print(f"[ERROR] Failed to list models: {list_resp.status_code}")
                print(list_resp.text[:500])
                return 
            
            models = list_resp.json().get('models', [])
            print("Available models:")
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f" - {m['name']}")
            
            # Simple match for 1.5-flash
            flash_model = next((m['name'] for m in models if 'gemini-1.5-flash' in m['name']), None)
             
            if not flash_model: 
                 print("[WARNING] gemini-1.5-flash not explicitly found in list. Using fallback 'models/gemini-1.5-flash'")
                 flash_model = "models/gemini-1.5-flash"
            else:
                 print(f"Found model: {flash_model}")

            print(f"\n[Step 2] Testing generation with {flash_model}...")
            gen_url = f"https://generativelanguage.googleapis.com/v1beta/{flash_model}:generateContent"
            
            payload = {
                "contents": [{
                    "parts": [{"text": "Reply with 'Connected'"}]
                }]
            }
            
            # Simple retry logic
            for i in range(3):
                gen_resp = await client.post(gen_url, params=params, json=payload)
                if gen_resp.status_code == 200:
                     print(f"[SUCCESS] {gen_resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
                     return
                elif gen_resp.status_code == 429:
                     print(f"[RATE LIMIT] Waiting 5s...")
                     await asyncio.sleep(5)
                else:
                     print(f"[ERROR] {gen_resp.status_code} - {gen_resp.text}")
                     break
                     
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_gemini_basic())
