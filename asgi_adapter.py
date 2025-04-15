"""ASGI adapter for FastAPI to work with Gunicorn."""

from asgiref.wsgi import WsgiToAsgi
from main import app as asgi_app

# Use the official asgiref adapter to convert our WSGI app to ASGI
# This creates a WSGI-compatible application from our ASGI FastAPI app
wsgi_app = WsgiToAsgi(asgi_app)