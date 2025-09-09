from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import time
from typing import Optional, List
from app.utils.logging import logger

router = APIRouter()

class SimpleImageRequest(BaseModel):
    text: str

class ImageEditRequest(BaseModel):
    text: str
    link: str

class MultiImageRequest(BaseModel):
    text: str
    links: str  # Comma-separated URLs

class ImageResponse(BaseModel):
    status: str
    url: str
    date: str
    dev: Optional[str] = None

class FluxProResponse(BaseModel):
    status: str
    images: List[str]
    date: str

# Gemini Image Generation and Editing
@router.post("/gemini-img", response_model=ImageResponse, summary="Gemini Pro Image Generation")
async def gemini_image_generate(request: SimpleImageRequest, req: Request):
    """
    Generate images using Gemini Pro
    
    - **text**: Image description prompt
    """
    base_url = "https://sii3.moayman.top/api/gemini-img.php"
    
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
        logger.error(f"Gemini image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")

@router.post("/gemini-img/edit", response_model=ImageResponse, summary="Gemini Pro Image Editing")
async def gemini_image_edit(request: ImageEditRequest, req: Request):
    """
    Edit images using Gemini Pro
    
    - **text**: Editing instructions/prompt
    - **link**: Image URL to edit
    """
    base_url = "https://sii3.moayman.top/api/gemini-img.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={
                "text": request.text,
                "link": request.link
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
        logger.error(f"Gemini image edit API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit image")

# GPT-5 Image Generation and Editing
@router.post("/gpt-img", response_model=ImageResponse, summary="GPT-5 Image Generation")
async def gpt_image_generate(request: SimpleImageRequest, req: Request):
    """
    Generate images using GPT-5
    
    - **text**: Image description prompt
    """
    base_url = "https://sii3.moayman.top/api/gpt-img.php"
    
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
        logger.error(f"GPT image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image")

@router.post("/gpt-img/edit", response_model=ImageResponse, summary="GPT-5 Image Editing")
async def gpt_image_edit(request: ImageEditRequest, req: Request):
    """
    Edit images using GPT-5
    
    - **text**: Editing instructions/prompt
    - **link**: Image URL to edit
    """
    base_url = "https://sii3.moayman.top/api/gpt-img.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={
                "text": request.text,
                "link": request.link
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
        logger.error(f"GPT image edit API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit image")

# Flux Pro - Generate 4 Images
@router.post("/flux-pro", response_model=FluxProResponse, summary="Flux Pro - Generate 4 Images")
async def flux_pro_generate(request: SimpleImageRequest, req: Request):
    """
    Generate 4 high-quality images using Flux Pro model
    
    - **text**: Image description prompt
    
    Returns 4 images per request with more powerful model
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

# High Quality Image Generation
@router.post("/img-cv", response_model=ImageResponse, summary="High Quality Image Generation")
async def img_cv_generate(request: SimpleImageRequest, req: Request):
    """
    Generate high-quality detailed images with incredible speed
    
    - **text**: Detailed image description
    
    Generates images within seconds with very high quality and details
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

# Nano Banana - Multi Image Merge
@router.post("/nano-banana", response_model=ImageResponse, summary="Nano Banana - Merge Multiple Images")
async def nano_banana_merge(request: MultiImageRequest, req: Request):
    """
    Merge multiple images using Nano Banana (up to 10 images)
    
    - **text**: Merge instruction/prompt
    - **links**: Comma-separated image URLs (max 10 images)
    
    Very fast API that supports merging 1 to 10 images in one request
    """
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