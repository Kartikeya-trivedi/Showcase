import os
from dotenv import load_dotenv

load_dotenv()
val = os.getenv('BACKEND_CORS_ORIGINS')
print(f"Raw Value: '{val}'")
print(f"Type: {type(val)}")
if val:
    for i, c in enumerate(val):
        print(f"{i}: {c} (ASCII: {ord(c)})")
