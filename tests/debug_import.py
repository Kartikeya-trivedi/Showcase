try:
    from app.main import app
    print("Portfolio model imported successfully")
except ImportError as e:
    print(f"ImportError details: {e}")
except Exception as e:
    print(f"Other error: {e}")
