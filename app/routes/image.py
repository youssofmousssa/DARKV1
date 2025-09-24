# app/routes/image.py
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
import httpx
import time
from typing import Optional, Dict, Any
from app.utils.logging import logger

router = APIRouter(prefix="/api")

# --- Models -----------------------------------------------------------------
class ImageEditRequest(BaseModel):
    text: str
    link: Optional[str] = None
    api_key: str

class SimpleImageRequest(BaseModel):
    text: str
    api_key: str

class MultiImageRequest(BaseModel):
    text: str
    links: Optional[str] = None  # comma-separated URLs, optional for generation mode
    api_key: str

class ImageResponse(BaseModel):
    date: str
    url: str
    dev: str

# --- Helpers ----------------------------------------------------------------
async def validate_api_key(api_key: str) -> bool:
    """
    Basic check for presence of API key.
    Expand this to verify against your DB or token service if needed.
    """
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

def _now_date_str() -> str:
    return time.strftime("%d/%m/%Y")

async def _post_and_parse(client: httpx.AsyncClient, url: str, data: Dict[str, Any], timeout: float = 60.0) -> ImageResponse:
    """
    Post to external URL and normalize response to ImageResponse.
    Handles both JSON responses and plain-text (URL) responses.
    """
    resp = await client.post(url, data=data, timeout=timeout)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "").lower()
    # If JSON-like response
    if content_type.startswith("application/json"):
        result = resp.json()
        # normalize keys
        date = result.get("date", _now_date_str())
        # try common fields for image link
        url_field = result.get("url") or result.get("image") or result.get("link") or result.get("data")
        dev = result.get("dev", "Don't forget to support the channel @DarkAIx")
        if not url_field:
            # If the JSON didn't include a direct URL, return the JSON as string in url field
            url_field = str(result)
        return ImageResponse(date=date, url=url_field, dev=dev)
    else:
        # plain-text response - treat as URL or raw string
        text = resp.text.strip()
        return ImageResponse(date=_now_date_str(), url=text, dev="Don't forget to support the channel @DarkAIx")

# --- Endpoints --------------------------------------------------------------
# NOTE: Gemini and GPT only support EDITING (which can also generate when link omitted).
# Removed any separate /gemini-img and /gpt-img generation endpoints per your instruction.

@router.post("/gemini-img/edit", response_model=ImageResponse, summary="Gemini Pro Image Editing")
async def gemini_image_edit(request: ImageEditRequest, req: Request):
    """
    Edit or generate (text-only) images using Gemini Pro.
    - text: editing instructions / prompt
    - link: optional image URL to edit; omit to generate a new image from prompt
    - api_key: required (validated locally)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/gemini-img.php"

    data = {"text": request.text}
    if request.link:
        data["link"] = request.link

    try:
        async with httpx.AsyncClient() as client:
            return await _post_and_parse(client, base_url, data, timeout=60.0)

    except httpx.TimeoutException as te:
        logger.error(f"Gemini image timeout: {te}")
        raise HTTPException(status_code=504, detail="External Gemini image API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"Gemini image HTTP error: {he} - response: {he.response.text if he.response is not None else 'no response'}")
        # surface the upstream status when appropriate
        raise HTTPException(status_code=502, detail=f"Gemini upstream error: {he.response.status_code if he.response is not None else 'unknown'}")
    except Exception as e:
        logger.error(f"Unexpected Gemini image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Gemini image request")


@router.post("/gpt-img/edit", response_model=ImageResponse, summary="GPT-5 Image Editing")
async def gpt_image_edit(request: ImageEditRequest, req: Request):
    """
    Edit or generate (text-only) images using GPT-5 image endpoint.
    - text: editing instructions / prompt
    - link: optional image URL to edit; omit to generate a new image from prompt
    - api_key: required (validated locally)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/gpt-img.php"

    data = {"text": request.text}
    if request.link:
        data["link"] = request.link

    try:
        async with httpx.AsyncClient() as client:
            return await _post_and_parse(client, base_url, data, timeout=60.0)

    except httpx.TimeoutException as te:
        logger.error(f"GPT image timeout: {te}")
        raise HTTPException(status_code=504, detail="External GPT image API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"GPT image HTTP error: {he} - response: {he.response.text if he.response is not None else 'no response'}")
        raise HTTPException(status_code=502, detail=f"GPT upstream error: {he.response.status_code if he.response is not None else 'unknown'}")
    except Exception as e:
        logger.error(f"Unexpected GPT image API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process GPT image request")


@router.post("/flux-pro", summary="Flux Pro - Generate 4 Images")
async def flux_pro_generate(request: SimpleImageRequest, req: Request):
    """
    Generate 4 high-quality images using Flux Pro model.
    Note: This endpoint returns the raw upstream response (JSON or text).
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/flux-pro.php"
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(base_url, data={"text": request.text})
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "").lower()
            if content_type.startswith("application/json"):
                return resp.json()
            else:
                return {"response": resp.text.strip()}
    except httpx.TimeoutException as te:
        logger.error(f"Flux Pro timeout: {te}")
        raise HTTPException(status_code=504, detail="Flux Pro API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"Flux Pro HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Flux Pro upstream error")
    except Exception as e:
        logger.error(f"Flux Pro unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Flux Pro images")


@router.post("/img-cv", response_model=ImageResponse, summary="High Quality Image Generation (img-cv)")
async def img_cv_generate(request: SimpleImageRequest, req: Request):
    """
    High quality image generation using img-cv API.
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/img-cv.php"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            return await _post_and_parse(client, base_url, {"text": request.text}, timeout=60.0)
    except httpx.TimeoutException as te:
        logger.error(f"img-cv timeout: {te}")
        raise HTTPException(status_code=504, detail="img-cv API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"img-cv HTTP error: {he}")
        raise HTTPException(status_code=502, detail="img-cv upstream error")
    except Exception as e:
        logger.error(f"img-cv unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate img-cv image")


async def _nano_banana_core_logic(text: str, links: Optional[str], api_key: str) -> ImageResponse:
    """
    Core logic for Nano Banana API - Generate or edit images.
    
    For image generation (text-to-image):
    - text: prompt for image generation (e.g., "Billie Eilish with Ronaldo")
    - links: omit or leave empty
    
    For image editing/merging:
    - text: editing instructions (e.g., "Merge the photos naturally")
    - links: comma-separated image URLs (max 10)
    """
    await validate_api_key(api_key)

    base_url = "https://sii3.top/api/nano-banana.php"
    data = {"text": text}

    # Check if this is editing mode (links provided) or generation mode (text only)
    if links and links.strip():
        # Image editing/merging mode
        links_list = [l.strip() for l in links.split(",") if l.strip()]
        
        if not links_list:
            raise HTTPException(status_code=400, detail="At least one link is required for editing mode")
        if len(links_list) > 10:
            raise HTTPException(status_code=400, detail="A maximum of 10 images is supported")
        
        data["links"] = ",".join(links_list)
        operation_type = "editing/merging"
    else:
        # Image generation mode (text only)
        operation_type = "generation"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            logger.info(f"Nano Banana {operation_type} request: {data}")
            return await _post_and_parse(client, base_url, data, timeout=120.0)

    except httpx.TimeoutException as te:
        logger.error(f"Nano Banana {operation_type} timeout: {te}")
        raise HTTPException(status_code=504, detail="Nano Banana API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"Nano Banana {operation_type} HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Nano Banana upstream error")
    except Exception as e:
        logger.error(f"Nano Banana {operation_type} unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process Nano Banana {operation_type} request")


@router.post("/nano-banana", response_model=ImageResponse, summary="Nano Banana - Generate or Edit Images (POST)")
async def nano_banana_post(request: MultiImageRequest, req: Request):
    """
    POST endpoint for Nano Banana - Generate or edit images.
    Accepts JSON body with text, optional links, and api_key.
    """
    return await _nano_banana_core_logic(request.text, request.links, request.api_key)


@router.get("/nano-banana", response_model=ImageResponse, summary="Nano Banana - Generate or Edit Images (GET)")
async def nano_banana_get(
    text: str = Query(..., description="Text prompt for generation or editing instructions"),
    links: Optional[str] = Query(None, description="Comma-separated image URLs (max 10, optional for generation)"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for Nano Banana - Generate or edit images.
    Accepts query parameters: text, links (optional), and api_key.
    """
    return await _nano_banana_core_logic(text, links, api_key)
