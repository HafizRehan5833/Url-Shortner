#!/usr/bin/env python3
"""Script to run the FastAPI application with Uvicorn."""

import uvicorn

if __name__ == "__main__":
    # Run the FastAPI app using the Starlette WSGI wrapper in main.py
    uvicorn.run("main:wsgi_app", host="0.0.0.0", port=5000, reload=True)