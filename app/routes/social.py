from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any
from app.utils.logging import logger

router = APIRouter()

class SocialDownloadRequest(BaseModel):
    url: str
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

@router.post("/social-downloader", summary="Universal Social Media Downloader")
async def download_social_content(request: SocialDownloadRequest, req: Request):
    """
    Download content from all social media platforms using a single API call
    
    - **url**: Social media URL to download content from
    - **api_key**: Your DarkAI API key (required)
    
    Supported platforms:
    - YouTube
    - TikTok  
    - Instagram
    - Facebook
    - Twitter/X
    - And many more social platforms...
    
    Simply provide the URL and get video/audio/image links instantly with quality and type information.
    No need for multiple tools or accounts.
    """
    await validate_api_key(request.api_key)
    
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/do.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(base_url, params={"url": request.url})
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Content not found or platform not supported")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=f"Download error: {e.response.text}")
    except Exception as e:
        logger.error(f"Social download API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to download content")
