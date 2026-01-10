from app.core.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Raw Env Var: {os.getenv('BACKEND_CORS_ORIGINS')}")

try:
    s = Settings()
    print("Settings loaded successfully")
    print(f"CORS: {s.BACKEND_CORS_ORIGINS}")
except Exception as e:
    print(f"Error loading settings: {e}")
