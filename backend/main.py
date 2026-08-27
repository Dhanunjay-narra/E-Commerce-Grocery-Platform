"""FreshCart FastAPI Production Application Entry Point."""
import uvicorn
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    workers = int(os.getenv("WEB_CONCURRENCY", 4))
    print(f"[*] Starting FreshCart E-Commerce Grocery Backend on {host}:{port} with {workers} workers...")
    uvicorn.run("app.main:app", host=host, port=port, reload=False, workers=workers)
