from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import List, Dict, Any
from app.utils.logging import logger

router = APIRouter()

class SocialDownloadRequest(BaseModel):
    url: str

class SocialDownloadResponse(BaseModel):
    status: str
    title: str
    downloads: List[Dict[str, Any]]

@router.post("/download", response_model=SocialDownloadResponse, summary="Universal Social Media Downloader")
async def download_social_content(request: SocialDownloadRequest, req: Request):
    """
    Download content from all social media platforms
    
    - **url**: Social media URL (YouTube, TikTok, Instagram, Facebook, Twitter, etc.)
    
    Supported platforms:
    - YouTube
    - TikTok
    - Instagram
    - Facebook
    - Twitter/X
    - And many more...
    
    Returns video/audio/image links with quality information
    """
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    base_url = "https://sii3.moayman.top/api/do.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(base_url, params={"url": request.url})
            response.raise_for_status()
            
            result = response.json()
            
            # Parse the response structure
            downloads = []
            if isinstance(result, dict):
                if "downloads" in result:
                    downloads = result["downloads"]
                elif "url" in result:
                    downloads = [{"url": result["url"], "type": "video", "quality": "default"}]
                elif "links" in result:
                    downloads = result["links"]
            
            title = result.get("title", "Downloaded Content")
            
            return SocialDownloadResponse(
                status="success",
                title=title,
                downloads=downloads
            )
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Content not found or platform not supported")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=f"Download error: {e.response.text}")
    except Exception as e:
        logger.error(f"Social download API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to download content")