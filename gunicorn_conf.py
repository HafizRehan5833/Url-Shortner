"""Gunicorn configuration file for FastAPI application."""

import multiprocessing

# Bind to host and port
bind = "0.0.0.0:5000"

# Number of worker processes
workers = 1  # Using a single worker for simplicity

# Worker class - use Uvicorn's worker class
worker_class = "uvicorn.workers.UvicornWorker"

# The application path - use the Starlette WSGI wrapper in main.py
wsgi_app = "main:wsgi_app"

# Reload workers when code changes (for development)
reload = True

# Logging
loglevel = "debug"

# Timeout
timeout = 120