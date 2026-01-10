import os
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
os.environ["GEMINI_API_KEY"] = "fake"
os.environ["SECRET_KEY"] = "fake"

try:
    from app.core.config import settings
    print(f"Loaded successfully: {settings.BACKEND_CORS_ORIGINS}")
    print(type(settings.BACKEND_CORS_ORIGINS))
except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()
