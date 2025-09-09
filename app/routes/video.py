from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class VideoRequest(BaseModel):
    text: str
    link: Optional[str] = None  # For image-to-video

class VideoResponse(BaseModel):
    status: str
    video_url: str
    processing_type: str  # "text-to-video" or "image-to-video"
    has_audio: bool

@router.post("/veo3", response_model=VideoResponse, summary="Text/Image to Video Generation")
async def generate_video(request: VideoRequest, req: Request):
    """
    Generate videos from text or convert images to videos with FREE audio support
    
    **Text-to-Video:**
    - **text**: Description of the video to create
    
    **Image-to-Video:**
    - **text**: Instructions for video conversion
    - **link**: Image URL to convert to video
    
    Features:
    - High-quality video generation
    - FREE audio support included
    - Fast processing
    - Cinematic effects support
    """
    base_url = "https://sii3.moayman.top/api/veo3.php"
    
    try:
        params = {"text": request.text}
        processing_type = "text-to-video"
        
        if request.link:
            params["link"] = request.link
            processing_type = "image-to-video"
        
        async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minutes timeout for video
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            
            video_url = result.get("url", result.get("video_url", ""))
            if not video_url and response.text.startswith("http"):
                video_url = response.text.strip()
            
            return VideoResponse(
                status="success",
                video_url=video_url,
                processing_type=processing_type,
                has_audio=True  # API includes free audio support
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Video generation timeout - please try again")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Video API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Video API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate video")