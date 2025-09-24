from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from app.utils.logging import logger

router = APIRouter()

class TextToVideoRequest(BaseModel):
    text: str
    api_key: str

class ImageToVideoRequest(BaseModel):
    text: str
    link: str
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

@router.post("/veo3/text-to-video", summary="Text to Video Generation")
async def text_to_video(request: TextToVideoRequest, req: Request):
    """
    Generate videos from text descriptions with FREE audio support
    
    - **text**: Description of the video to create
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - High-quality video generation from text
    - FREE audio support included
    - Fast processing
    - Cinematic effects support
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/veo3.php"
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"video_url": response.text.strip()}
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Video generation timeout - please try again")
    except Exception as e:
        logger.error(f"Text-to-video API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate video")

@router.post("/veo3/image-to-video", summary="Image to Video Conversion")
async def image_to_video(request: ImageToVideoRequest, req: Request):
    """
    Convert images to videos with FREE audio support
    
    - **text**: Instructions for video conversion
    - **link**: Image URL to convert to video
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Convert static images to dynamic videos
    - FREE audio support included
    - Cinematic effects and animations
    - Fast processing
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/veo3.php"
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(base_url, data={
                "text": request.text,
                "link": request.link
            })
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"video_url": response.text.strip()}
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Video conversion timeout - please try again")
    except Exception as e:
        logger.error(f"Image-to-video API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert image to video")
