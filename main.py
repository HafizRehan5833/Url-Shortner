import logging
import os
import random
import string
import time
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl, Field
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="URL Shortener Service")

# For WSGI servers like Gunicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware import Middleware
from pathlib import Path

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Create a wrapper Starlette application
wsgi_app = Starlette(
    routes=[
        Mount("/", app=app)
    ],
    middleware=[
        Middleware(CORSMiddleware,
                  allow_origins=["*"],
                  allow_credentials=True,
                  allow_methods=["*"],
                  allow_headers=["*"])
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# In-memory storage for URL mappings
# Structure: {short_code: {"original_url": url, "created_at": timestamp, "clicks": 0}}
url_db: Dict[str, Dict] = {}

# In-memory rate limiting
rate_limits: Dict[str, Dict[str, int]] = {}

# Constants
SHORTENED_URL_LENGTH = 6
MAX_REQUESTS_PER_MINUTE = 60


class URLInput(BaseModel):
    url: HttpUrl = Field(..., description="Original URL to be shortened")


class URLOutput(BaseModel):
    original_url: str
    shortened_url: str
    created_at: str
    clicks: int = 0


# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        # Only rate limit the creation endpoint
        if request.url.path == "/api/shorten" and request.method == "POST":
            current_time = int(time.time())
            
            # Initialize or update rate limit data for this IP
            if client_ip not in rate_limits:
                rate_limits[client_ip] = {"requests": 0, "reset_at": current_time + 60}
            
            # Check if we need to reset the counter
            if current_time > rate_limits[client_ip]["reset_at"]:
                rate_limits[client_ip] = {"requests": 0, "reset_at": current_time + 60}
            
            # Check rate limit
            if rate_limits[client_ip]["requests"] >= MAX_REQUESTS_PER_MINUTE:
                return HTMLResponse(
                    content="Rate limit exceeded. Please try again later.",
                    status_code=429
                )
            
            # Increment request counter
            rate_limits[client_ip]["requests"] += 1
        
        response = await call_next(request)
        return response


app.add_middleware(RateLimitMiddleware)


def generate_short_code() -> str:
    """Generate a random short code for the URL."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(SHORTENED_URL_LENGTH))
        if code not in url_db:
            return code


def validate_url(url: str) -> bool:
    """Validate if the URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the home page."""
    return templates.TemplateResponse(r"index.html", {"request": request})


@app.post("/api/shorten", response_model=URLOutput)
async def create_short_url(url_input: URLInput):
    """Create a shortened URL."""
    original_url = str(url_input.url)
    
    if not validate_url(original_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Check if this URL has already been shortened
    for code, data in url_db.items():
        if data["original_url"] == original_url:
            # Return existing shortened URL
            return URLOutput(
                original_url=original_url,
                shortened_url=f"{code}",
                created_at=data["created_at"],
                clicks=data["clicks"]
            )
    
    # Generate a new short code
    short_code = generate_short_code()
    
    # Store the URL mapping
    url_db[short_code] = {
        "original_url": original_url,
        "created_at": datetime.now().isoformat(),
        "clicks": 0
    }
    
    logger.debug(f"Created shortened URL: {short_code} -> {original_url}")
    
    return URLOutput(
        original_url=original_url,
        shortened_url=f"{short_code}",
        created_at=url_db[short_code]["created_at"],
        clicks=0
    )


@app.post("/shorten", response_class=HTMLResponse)
async def shorten_url_form(request: Request, url: str = Form(...)):
    """Handle URL shortening from the form submission."""
    if not validate_url(url):
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": "Invalid URL format. Please provide a valid URL."}
        )
    
    url_input = URLInput(url=url)
    short_url_info = await create_short_url(url_input)
    
    # Get the base URL for the shortened link
    base_url = str(request.base_url).rstrip('/')
    full_short_url = f"{base_url}/{short_url_info.shortened_url}"
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "short_url": full_short_url,
            "original_url": url,
            "success": True
        }
    )


@app.get("/{short_code}")
async def redirect_to_original(short_code: str):
    """Redirect to the original URL when a shortened URL is accessed."""
    if short_code not in url_db:
        raise HTTPException(status_code=404, detail="Shortened URL not found")
    
    # Increment click count
    url_db[short_code]["clicks"] += 1
    
    # Redirect to the original URL
    return RedirectResponse(url=url_db[short_code]["original_url"])


@app.get("/api/stats/{short_code}", response_model=URLOutput)
async def get_url_stats(short_code: str):
    """Get statistics for a shortened URL."""
    if short_code not in url_db:
        raise HTTPException(status_code=404, detail="Shortened URL not found")
    
    url_data = url_db[short_code]
    
    return URLOutput(
        original_url=url_data["original_url"],
        shortened_url=f"{short_code}",
        created_at=url_data["created_at"],
        clicks=url_data["clicks"]
    )


if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
    
# For Gunicorn compatibility, reference wsgi_app instead of app
# Usage: gunicorn main:wsgi_app
