from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional, List
from app.utils.logging import logger

router = APIRouter()

class ImageRequest(BaseModel):
    text: str
    link: Optional[str] = None
    links: Optional[str] = None  # For nano-banana (comma-separated)

class ImageResponse(BaseModel):
    status: str
    url: str
    date: str
    dev: Optional[str] = None

class FluxProResponse(BaseModel):
    status: str
    images: List[str]
    date: str

@router.post("/gemini-img", response_model=ImageResponse, summary="Gemini Pro Image Generation/Editing")
async def gemini_image(request: ImageRequest, req: Request):
    """
    Generate or edit images using Gemini Pro
    
    - **text**: Description or editing prompt
    - **link**: Optional image URL to edit
    """
    base_url = "https://sii3.moayman.top/api/gemini-img.php"
    
    try:
        params = {"text": request.text}
        if request.link:
            params["link"] = request.link
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            result = response.json()
            
            return ImageResponse(
                status="success",
                url=result.get("url", ""),
                date=result.get("date", ""),
                dev=result.get("dev", "")
            )
            
    except Exception as e:
        logger.error(f"Gemini image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")

@router.post("/gpt-img", response_model=ImageResponse, summary="GPT-5 Image Generation/Editing")
async def gpt_image(request: ImageRequest, req: Request):
    """
    Generate or edit images using GPT-5
    
    - **text**: Description or editing prompt
    - **link**: Optional image URL to edit
    """
    base_url = "https://sii3.moayman.top/api/gpt-img.php"
    
    try:
        params = {"text": request.text}
        if request.link:
            params["link"] = request.link
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            result = response.json()
            
            return ImageResponse(
                status="success",
                url=result.get("url", ""),
                date=result.get("date", ""),
                dev=result.get("dev", "")
            )
            
    except Exception as e:
        logger.error(f"GPT image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")

@router.post("/flux-pro", response_model=FluxProResponse, summary="Flux Pro - 4 Images Generation")
async def flux_pro_image(request: ImageRequest, req: Request):
    """
    Generate 4 high-quality images using Flux Pro model
    
    - **text**: Image description prompt
    """
    base_url = "https://sii3.moayman.top/api/flux-pro.php"
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json()
            
            # Extract image URLs from response
            images = []
            if isinstance(result, dict):
                # Handle different response formats
                if "images" in result:
                    images = result["images"]
                elif "url" in result:
                    images = [result["url"]]
                elif "urls" in result:
                    images = result["urls"]
            
            return FluxProResponse(
                status="success",
                images=images,
                date=result.get("date", "")
            )
            
    except Exception as e:
        logger.error(f"Flux Pro API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate images")

@router.post("/nano-banana", response_model=ImageResponse, summary="Nano Banana - Multi Image Merge")
async def nano_banana_merge(request: ImageRequest, req: Request):
    """
    Merge multiple images using Nano Banana (up to 10 images)
    
    - **text**: Merge instruction/prompt
    - **links**: Comma-separated image URLs (max 10)
    """
    if not request.links:
        raise HTTPException(status_code=400, detail="Image links are required")
    
    base_url = "https://sii3.moayman.top/api/nano-banana.php"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(base_url, data={
                "text": request.text,
                "links": request.links
            })
            response.raise_for_status()
            
            result = response.json()
            
            return ImageResponse(
                status="success",
                url=result.get("url", ""),
                date=result.get("date", ""),
                dev=result.get("dev", "")
            )
            
    except Exception as e:
        logger.error(f"Nano Banana API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to merge images")

@router.post("/img-cv", response_model=ImageResponse, summary="High Quality Image Generation")
async def image_cv_generate(request: ImageRequest, req: Request):
    """
    Generate high-quality detailed images with incredible speed
    
    - **text**: Detailed image description
    """
    base_url = "https://sii3.moayman.top/api/img-cv.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json()
            
            return ImageResponse(
                status="success",
                url=result.get("url", ""),
                date=result.get("date", ""),
                dev=result.get("dev", "")
            )
            
    except Exception as e:
        logger.error(f"Image CV API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")