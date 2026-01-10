"""
Standalone Gemini API Connection Test Script
Run this to verify your API key and model access before starting the server.
Usage: python test_gemini_connection.py
"""

import asyncio
import sys
import os
import httpx

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.core.config import settings

async def test_gemini():
    print("=" * 50)
    print("GEMINI API CONNECTION TEST")
    print("=" * 50)
    
    # Check API key
    if not settings.GEMINI_API_KEY:
        print("\n[ERROR] GEMINI_API_KEY not found in .env file!")
        return False
    
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
                return False
            
            models = list_resp.json().get('models', [])
            flash_models = [m['name'] for m in models if 'flash' in m.get('name', '').lower()]
            
            print(f"Found {len(models)} models total.")
            print(f"Flash models available: {flash_models[:5]}")  # Show first 5
            
            # Pick best available model - use exact names from API
            chosen_model = None
            for m in models:
                name = m.get('name', '')
                if 'gemini-2.0-flash' in name or 'gemini-1.5-flash' in name:
                    chosen_model = name
                    break
            
            if not chosen_model and flash_models:
                chosen_model = flash_models[0]
            
            if not chosen_model:
                print("[ERROR] No suitable flash model found!")
                return False
            
            print(f"\nChosen model: {chosen_model}")
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch models: {e}")
            return False
        
        # Step 2: Test generation
        print("\n[Step 2] Testing text generation...")
        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{chosen_model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": "Say 'Hello, World!' and nothing else."}]
            }]
        }
        
        try:
            for attempt in range(3):
                gen_resp = await client.post(gen_url, params=params, json=payload)
                
                if gen_resp.status_code == 200:
                    data = gen_resp.json()
                    text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    print(f"[SUCCESS] Response: {text.strip()}")
                    print("\n" + "=" * 50)
                    print("CONNECTION TEST PASSED!")
                    print(f"Recommended model for your app: {chosen_model}")
                    print("=" * 50)
                    return chosen_model
                elif gen_resp.status_code == 429:
                    print(f"[RATE LIMITED] Attempt {attempt+1}/3. Waiting 20 seconds...")
                    await asyncio.sleep(20)
                else:
                    print(f"[ERROR] Generation failed: {gen_resp.status_code}")
                    print(f"Full error response: {gen_resp.text}")
                    return False
            
            print("[ERROR] Rate limited after 3 attempts. Try again later.")
            return False
                
        except Exception as e:
            print(f"[ERROR] Generation request failed: {e}")
            return False

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    result = asyncio.run(test_gemini())
    
    if result:
        print(f"\nTo use this model, update your .env or config:")
        print(f'  GEMINI_VISION_MODEL="{result.replace("models/", "")}"')
        print(f'  GEMINI_AGENT_MODEL="{result.replace("models/", "")}"')
    else:
        print("\n[FAILED] Please check your API key and network connection.")
    
    sys.exit(0 if result else 1)
