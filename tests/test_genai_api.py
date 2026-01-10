"""
Test script to verify google.genai API structure and usage.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def test_genai_api():
    """Test the google.genai API structure."""
    try:
        import google.genai as genai
        from google.genai import types
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("[ERROR] GEMINI_API_KEY not found in environment")
            return
        
        print(f"[OK] API Key found: {api_key[:10]}...")
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        print(f"[OK] Client created: {type(client)}")
        
        # Check client attributes
        print(f"\n[INFO] Client attributes:")
        attrs = [attr for attr in dir(client) if not attr.startswith('_')]
        for attr in attrs[:20]:  # First 20
            print(f"   - {attr}")
        
        # Check if aio exists
        if hasattr(client, 'aio'):
            print(f"\n[OK] Client has 'aio' attribute: {type(client.aio)}")
            aio_attrs = [attr for attr in dir(client.aio) if not attr.startswith('_')]
            print(f"   aio attributes: {aio_attrs}")
            
            if hasattr(client.aio, 'models'):
                print(f"\n[OK] Client.aio has 'models' attribute: {type(client.aio.models)}")
                models_attrs = [attr for attr in dir(client.aio.models) if not attr.startswith('_')]
                print(f"   models attributes: {models_attrs}")
                
                # Try to call generate_content
                if 'generate_content' in models_attrs:
                    print(f"\n[OK] Found generate_content method!")
                    print(f"   Trying to inspect method signature...")
                    import inspect
                    sig = inspect.signature(client.aio.models.generate_content)
                    print(f"   Signature: {sig}")
                else:
                    print(f"\n[ERROR] generate_content not found in models")
            else:
                print(f"\n[ERROR] Client.aio does not have 'models' attribute")
        else:
            print(f"\n[ERROR] Client does not have 'aio' attribute")
            print(f"   Available attributes: {attrs}")
        
        # Alternative: Check if there's a different way to call async
        print(f"\n[INFO] Checking for alternative async methods...")
        if hasattr(client, 'models'):
            print(f"[OK] Client has 'models' attribute")
            models_attrs = [attr for attr in dir(client.models) if not attr.startswith('_')]
            print(f"   models attributes: {models_attrs}")
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("   Make sure google-genai is installed: pip install google-genai")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_genai_api())
