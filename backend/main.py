from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import time
import traceback
import asyncio
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the directory where this file is located
_current_dir = Path(__file__).parent
_root_dir = _current_dir.parent
load_dotenv(_root_dir / ".env")

from backend.services.prompt_template import PromptTemplateService
from backend.services.gemini_service import GeminiService
from backend.services.youtube_service import YouTubeService
from backend.services.discord_service import DiscordWebhookService

app = FastAPI(title="Dynamic Prompt Template App", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend directory is one level up)
_frontend_dir = _root_dir / "frontend"
app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")

# Helper functions for smart Discord logging
def _is_automated_request(user_agent: str, referer: str) -> bool:
    """Detect if request is from automated tools/bots"""
    automated_indicators = [
        "bot", "crawler", "spider", "monitor", "health", "uptime",
        "pingdom", "newrelic", "datadog", "nagios", "zabbix",
        "curl", "wget", "python-requests", "go-http-client",
        "postman", "insomnia", "httpie"
    ]
    
    user_agent_lower = user_agent.lower()
    return any(indicator in user_agent_lower for indicator in automated_indicators)

def _is_user_initiated_request(user_agent: str, referer: str) -> bool:
    """Detect if request is likely user-initiated"""
    # If it's from a browser with a referer from our domain, it's likely user-initiated
    if referer and any(domain in referer for domain in ["localhost", "127.0.0.1", "prompt-template"]):
        browser_indicators = ["mozilla", "chrome", "firefox", "safari", "edge", "opera"]
        user_agent_lower = user_agent.lower()
        return any(browser in user_agent_lower for browser in browser_indicators)
    
    # If no referer but it's a browser, could be direct access
    if not referer:
        browser_indicators = ["mozilla", "chrome", "firefox", "safari", "edge", "opera"]
        user_agent_lower = user_agent.lower()
        return any(browser in user_agent_lower for browser in browser_indicators)
    
    return False

# Middleware for Discord logging
@app.middleware("http")
async def discord_logging_middleware(request: Request, call_next):
    """Middleware to log all requests to Discord webhook"""
    start_time = time.time()
    
    # Get user details
    user_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    referer = request.headers.get("referer", "")
    
    # For the main page visit, log as visitor (fire and forget - don't block)
    if request.url.path == "/" and request.method == "GET":
        asyncio.create_task(discord_service.send_visitor_log(user_ip, user_agent, referer))
    
    # Get request body for logging (if applicable)
    request_data = None
    if request.method in ["POST", "PUT", "PATCH"] and "api" in request.url.path:
        try:
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
        except:
            request_data = {"body": "Unable to parse request body"}
    
    response = None
    status_code = 500
    response_data = None
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Don't capture response body - it's slow and blocks the response
        # Discord logging doesn't need the full response anyway
        response_data = None
        
    except Exception as e:
        status_code = 500
        response = Response(
            content=json.dumps({"error": "Internal server error"}),
            status_code=500,
            media_type="application/json"
        )
        
        # Log error to Discord (fire and forget - don't block response)
        asyncio.create_task(discord_service.send_error_log(
            str(e), 
            f"{request.method} {request.url.path}",
            user_ip,
            traceback.format_exc()
        ))
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Define endpoints to exclude from Discord logging (automated/monitoring calls)
    excluded_endpoints = [
        "/api/quota_status",  # Health check/monitoring endpoint
        "/api/quotas",        # Only log quotas if it's a user-initiated request
        "/api/health",        # Health check endpoint
        "/api/status"         # Status endpoint
    ]
    
    # Smart filtering: Log request to Discord only for meaningful user interactions
    should_log = (
        "/api/" in request.url.path and 
        request.url.path not in excluded_endpoints and
        not _is_automated_request(user_agent, referer)
    )
    
    # Special case: Log quota requests only if they seem to be user-initiated
    if request.url.path in ["/api/quotas", "/api/quota_status"]:
        should_log = _is_user_initiated_request(user_agent, referer)
    
    if should_log:
        # Fire and forget - don't block the response waiting for Discord
        asyncio.create_task(discord_service.send_request_log(
            request.method,
            request.url.path,
            user_ip,
            user_agent,
            status_code,
            response_data,
            request_data,
            processing_time
        ))
    
    return response

# Initialize services
prompt_service = PromptTemplateService()
gemini_service = GeminiService()
youtube_service = YouTubeService()
discord_service = DiscordWebhookService()

# Request models
class TopicRequest(BaseModel):
    topic: str

class APIKeyRequest(BaseModel):
    gemini_key: Optional[str] = None
    youtube_key: Optional[str] = None

class GeminiRequest(BaseModel):
    topic: str
    prompt: str
    api_key: Optional[str] = None

class YouTubeRequest(BaseModel):
    topic: str
    api_key: Optional[str] = None
    max_results: Optional[int] = 60

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend HTML page"""
    frontend_path = _root_dir / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/generate-prompt")
async def generate_prompt(request: TopicRequest):
    """Generate a dynamic prompt template for the given topic"""
    try:
        prompt_data = prompt_service.generate_prompt(request.topic)
        return {
            "success": True,
            "data": prompt_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating prompt: {str(e)}")

@app.post("/api/gemini/query")
async def query_gemini(request: GeminiRequest):
    """Query Gemini API with the generated prompt"""
    try:
        response = await gemini_service.query(
            prompt=request.prompt,
            api_key=request.api_key
        )
        return {
            "success": True,
            "data": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Gemini: {str(e)}")

@app.post("/api/youtube/search")
async def search_youtube(request: YouTubeRequest):
    """Search YouTube for videos related to the topic"""
    try:
        response = await youtube_service.search_videos(
            topic=request.topic,
            api_key=request.api_key,
            max_results=request.max_results or 60
        )
        return {
            "success": True,
            "data": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {str(e)}")

@app.get("/api/quotas")
async def get_api_quotas():
    """Get current API quota status for both services"""
    try:
        gemini_quota = await gemini_service.get_quota_info()
        youtube_quota = await youtube_service.get_quota_info()
        
        return {
            "success": True,
            "data": {
                "gemini": gemini_quota,
                "youtube": youtube_quota
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quotas: {str(e)}")

@app.get("/api/quota_status")
async def get_quota_status():
    """Alternative endpoint for quota status (for backward compatibility)"""
    return await get_api_quotas()

@app.post("/api/update-keys")
async def update_api_keys(request: APIKeyRequest):
    """Update API keys for the services"""
    try:
        updated = {}
        if request.gemini_key:
            gemini_service.update_api_key(request.gemini_key)
            updated["gemini"] = True
        if request.youtube_key:
            youtube_service.update_api_key(request.youtube_key)
            updated["youtube"] = True
            
        return {
            "success": True,
            "data": {"updated_keys": updated},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating keys: {str(e)}")

@app.get("/api/health")
async def api_health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "gemini": bool(gemini_service.api_key),
            "youtube": bool(youtube_service.api_key),
            "discord": bool(discord_service.webhook_url)
        }
    }

@app.get("/api/topics/examples")
async def get_example_topics():
    """Get example topics for the dropdown"""
    examples = [
        "Prompt Engineering",
        "Python for Data Science",
        "Machine Learning Fundamentals",
        "Web Development with React",
        "DevOps and CI/CD",
        "Cloud Computing with AWS",
        "Cybersecurity Basics",
        "Digital Marketing",
        "Blockchain Technology",
        "Artificial Intelligence Ethics"
    ]
    return {
        "success": True,
        "data": examples,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)