from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from app.utils.logging import logger

router = APIRouter()

class BackgroundRemovalRequest(BaseModel):
    url: str
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

@router.post("/remove-bg", summary="Remove Background from Image")
async def remove_background(request: BackgroundRemovalRequest, req: Request):
    """
    Remove background from images automatically
    
    - **url**: Image URL to process
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Automatic background detection and removal
    - Returns processed image with transparent background
    - Supports common image formats (JPG, PNG, etc.)
    - Fast processing
    """
    await validate_api_key(request.api_key)
    
    if not request.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/remove-bg.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(base_url, params={"url": request.url})
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"processed_url": response.text.strip()}
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Image not found or invalid format")
        else:
            raise HTTPException(status_code=e.response.status_code, detail=f"Background removal error: {e.response.text}")
    except Exception as e:
        logger.error(f"Background removal API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove background")
