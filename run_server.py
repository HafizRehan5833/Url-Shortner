"""Script to run the URL shortener service with Uvicorn."""

import uvicorn

if __name__ == "__main__":
    print("Starting URL Shortener service with ASGI server (Uvicorn)...")
    # Use the FastAPI app directly, not the wsgi wrapper
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)