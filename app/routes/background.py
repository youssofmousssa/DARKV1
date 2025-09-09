from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from app.utils.logging import logger

router = APIRouter()

class BackgroundRemovalRequest(BaseModel):
    url: str

class BackgroundRemovalResponse(BaseModel):
    status: str
    original_url: str
    processed_url: str

@router.post("/remove-bg", response_model=BackgroundRemovalResponse, summary="Remove Background from Image")
async def remove_background(request: BackgroundRemovalRequest, req: Request):
    """
    Remove background from images automatically
    
    - **url**: Image URL to process
    
    Features:
    - Automatic background detection and removal
    - Returns processed image with transparent background
    - Supports common image formats (JPG, PNG, etc.)
    - Fast processing
    """
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.moayman.top/api/remove-bg.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(base_url, params={"url": request.url})
            response.raise_for_status()
            
            # Handle different response types
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
                processed_url = result.get("url", result.get("processed_url", ""))
            else:
                # If response is direct image URL
                processed_url = response.url if response.status_code == 200 else ""
            
            if not processed_url and response.text.startswith("http"):
                processed_url = response.text.strip()
            
            return BackgroundRemovalResponse(
                status="success",
                original_url=request.url,
                processed_url=str(processed_url)
            )
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Image not found or invalid format")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=f"Background removal error: {e.response.text}")
    except Exception as e:
        logger.error(f"Background removal API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove background")