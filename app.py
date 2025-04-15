"""Main entry point for the URL shortener application."""

from main import app as fastapi_app

# This variable is used by Gunicorn to find the ASGI application
app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)