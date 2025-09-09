from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from app.utils.logging import logger

router = APIRouter()

class TextToVideoRequest(BaseModel):
    text: str

class ImageToVideoRequest(BaseModel):
    text: str
    link: str

class VideoResponse(BaseModel):
    status: str
    video_url: str
    processing_type: str
    has_audio: bool

@router.post("/veo3/text-to-video", response_model=VideoResponse, summary="Text to Video Generation")
async def text_to_video(request: TextToVideoRequest, req: Request):
    """
    Generate videos from text descriptions with FREE audio support
    
    - **text**: Description of the video to create
    
    Features:
    - High-quality video generation from text
    - FREE audio support included
    - Fast processing
    - Cinematic effects support
    """
    base_url = "https://sii3.moayman.top/api/veo3.php"
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            
            video_url = result.get("url", result.get("video_url", ""))
            if not video_url and response.text.startswith("http"):
                video_url = response.text.strip()
            
            return VideoResponse(
                status="success",
                video_url=video_url,
                processing_type="text-to-video",
                has_audio=True
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Video generation timeout - please try again")
    except Exception as e:
        logger.error(f"Text-to-video API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate video")

@router.post("/veo3/image-to-video", response_model=VideoResponse, summary="Image to Video Conversion")
async def image_to_video(request: ImageToVideoRequest, req: Request):
    """
    Convert images to videos with FREE audio support
    
    - **text**: Instructions for video conversion
    - **link**: Image URL to convert to video
    
    Features:
    - Convert static images to dynamic videos
    - FREE audio support included
    - Cinematic effects and animations
    - Fast processing
    """
    base_url = "https://sii3.moayman.top/api/veo3.php"
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(base_url, data={
                "text": request.text,
                "link": request.link
            })
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            
            video_url = result.get("url", result.get("video_url", ""))
            if not video_url and response.text.startswith("http"):
                video_url = response.text.strip()
            
            return VideoResponse(
                status="success",
                video_url=video_url,
                processing_type="image-to-video",
                has_audio=True
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Video conversion timeout - please try again")
    except Exception as e:
        logger.error(f"Image-to-video API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert image to video")