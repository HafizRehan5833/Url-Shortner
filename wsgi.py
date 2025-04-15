"""WSGI application entry point for gunicorn."""

# Import the adapter application
from asgi_adapter import wsgi_app

# This is the WSGI application for Gunicorn
app = wsgi_app

if __name__ == "__main__":
    # For direct running with Python (not recommended for production)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)