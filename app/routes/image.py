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

# New models for DarkAI APIs
class ImageGenerationRequest(BaseModel):
    text: str
    size: Optional[str] = "1024x1024"  # Available: 1024x1024, 1792x1024, 1024x1792
    api_key: str

class ImageQualityRequest(BaseModel):
    link: str  # Image URL to enhance
    api_key: str

class SeedReam4Request(BaseModel):
    text: str
    links: Optional[str] = None  # comma-separated URLs, max 4 for editing
    api_key: str

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


# --- New DarkAI API Functions ----------------------------------------------

async def _get_and_parse(client: httpx.AsyncClient, url: str, params: Dict[str, Any], timeout: float = 60.0) -> ImageResponse:
    """
    GET request to external URL and normalize response to ImageResponse.
    Handles both JSON responses and plain-text (URL) responses.
    """
    resp = await client.get(url, params=params, timeout=timeout)
    resp.raise_for_status()

    content_type = resp.headers.get("content-type", "").lower()
    if content_type.startswith("application/json"):
        result = resp.json()
        date = result.get("date", _now_date_str())
        url_field = result.get("url") or result.get("image") or result.get("link") or result.get("data")
        dev = result.get("dev", "Don't forget to support the channel @DarkAIx")
        if not url_field:
            url_field = str(result)
        return ImageResponse(date=date, url=url_field, dev=dev)
    else:
        text = resp.text.strip()
        return ImageResponse(date=_now_date_str(), url=text, dev="Don't forget to support the channel @DarkAIx")

# --- New DarkAI API Endpoints ----------------------------------------------

@router.post("/img-bo", response_model=ImageResponse, summary="Ultra-Realistic Image Generation")
async def img_bo_generate_post(request: ImageGenerationRequest, req: Request):
    """
    Generate ultra-realistic, high-quality images with amazing details using img-bo API.
    
    - **text**: Description of the image to generate
    - **size**: Image dimensions (1024x1024, 1792x1024, 1024x1792)
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Ultra-realistic, high-quality images in seconds
    - Amazing detail and color accuracy
    - Multiple size options available
    - Fast processing
    """
    await validate_api_key(request.api_key)
    
    # Validate size parameter
    valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
    if request.size not in valid_sizes:
        raise HTTPException(status_code=400, detail=f"Invalid size. Available sizes: {', '.join(valid_sizes)}")
    
    base_url = "https://sii3.top/api/img-bo.php"
    data = {"text": request.text, "size": request.size}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _post_and_parse(client, base_url, data, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"img-bo timeout: {te}")
        raise HTTPException(status_code=504, detail="Image generation API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"img-bo HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Image generation upstream error")
    except Exception as e:
        logger.error(f"img-bo unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate ultra-realistic image")

@router.get("/img-bo", response_model=ImageResponse, summary="Ultra-Realistic Image Generation (GET)")
async def img_bo_generate_get(
    text: str = Query(..., description="Description of the image to generate"),
    size: str = Query("1024x1024", description="Image dimensions (1024x1024, 1792x1024, 1024x1792)"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for ultra-realistic image generation using img-bo API.
    Example: /api/img-bo?text=cat+with+sunglasses&size=1024x1024&api_key=YOUR_KEY
    """
    # Validate size parameter
    valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
    if size not in valid_sizes:
        raise HTTPException(status_code=400, detail=f"Invalid size. Available sizes: {', '.join(valid_sizes)}")
    
    await validate_api_key(api_key)
    base_url = "https://sii3.top/api/img-bo.php"
    params = {"text": text, "size": size}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _get_and_parse(client, base_url, params, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"img-bo GET timeout: {te}")
        raise HTTPException(status_code=504, detail="Image generation API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"img-bo GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Image generation upstream error")
    except Exception as e:
        logger.error(f"img-bo GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate ultra-realistic image")

@router.post("/quality-enhance", response_model=ImageResponse, summary="AI Image Quality Enhancement")
async def quality_enhance_post(request: ImageQualityRequest, req: Request):
    """
    Improve image quality, details, colors up to 8K resolution with artificial intelligence.
    
    - **link**: URL of the image to enhance
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Enhance image quality up to 8K resolution
    - Improve details and color accuracy
    - AI-powered enhancement using GPT-5 model
    - Fast processing
    """
    await validate_api_key(request.api_key)
    
    if not request.link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/quality.php"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            return await _get_and_parse(client, base_url, {"link": request.link}, timeout=120.0)
    except httpx.TimeoutException as te:
        logger.error(f"Quality enhancement timeout: {te}")
        raise HTTPException(status_code=504, detail="Image enhancement API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"Quality enhancement HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Image enhancement upstream error")
    except Exception as e:
        logger.error(f"Quality enhancement unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enhance image quality")

@router.get("/quality-enhance", response_model=ImageResponse, summary="AI Image Quality Enhancement (GET)")
async def quality_enhance_get(
    link: str = Query(..., description="URL of the image to enhance"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for AI image quality enhancement.
    Example: /api/quality-enhance?link=https://example.com/image.jpg&api_key=YOUR_KEY
    """
    await validate_api_key(api_key)
    
    if not link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/quality.php"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            return await _get_and_parse(client, base_url, {"link": link}, timeout=120.0)
    except httpx.TimeoutException as te:
        logger.error(f"Quality enhancement GET timeout: {te}")
        raise HTTPException(status_code=504, detail="Image enhancement API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"Quality enhancement GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="Image enhancement upstream error")
    except Exception as e:
        logger.error(f"Quality enhancement GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enhance image quality")

@router.post("/gpt-imager/create", response_model=ImageResponse, summary="GPT-IMAGER - Create Image from Text")
async def gpt_imager_create_post(request: SimpleImageRequest, req: Request):
    """
    Create images from text using the GPT-IMAGER model API.
    
    - **text**: Description of the image to create
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Advanced text-to-image generation
    - High-quality results
    - Fast processing
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/gpt-img.php"
    data = {"text": request.text}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _post_and_parse(client, base_url, data, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"GPT-IMAGER create timeout: {te}")
        raise HTTPException(status_code=504, detail="GPT-IMAGER API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"GPT-IMAGER create HTTP error: {he}")
        raise HTTPException(status_code=502, detail="GPT-IMAGER upstream error")
    except Exception as e:
        logger.error(f"GPT-IMAGER create unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create image with GPT-IMAGER")

@router.get("/gpt-imager/create", response_model=ImageResponse, summary="GPT-IMAGER - Create Image from Text (GET)")
async def gpt_imager_create_get(
    text: str = Query(..., description="Description of the image to create"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for GPT-IMAGER image creation.
    Example: /api/gpt-imager/create?text=Minecraft-world&api_key=YOUR_KEY
    """
    await validate_api_key(api_key)
    base_url = "https://sii3.top/api/gpt-img.php"
    params = {"text": text}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _get_and_parse(client, base_url, params, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"GPT-IMAGER create GET timeout: {te}")
        raise HTTPException(status_code=504, detail="GPT-IMAGER API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"GPT-IMAGER create GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="GPT-IMAGER upstream error")
    except Exception as e:
        logger.error(f"GPT-IMAGER create GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create image with GPT-IMAGER")

@router.post("/gpt-imager/edit", response_model=ImageResponse, summary="GPT-IMAGER - Edit Image")
async def gpt_imager_edit_post(request: ImageEditRequest, req: Request):
    """
    Edit existing images using the GPT-IMAGER model API.
    
    - **text**: Editing instructions (e.g., "Make the icon gold")
    - **link**: URL of the image to edit
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Advanced image editing capabilities
    - Intelligent modifications based on text instructions
    - High-quality results
    """
    await validate_api_key(request.api_key)
    
    if not request.link:
        raise HTTPException(status_code=400, detail="Image link is required for editing")
    
    if not request.link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/gpt-img.php"
    data = {"text": request.text, "link": request.link}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _post_and_parse(client, base_url, data, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"GPT-IMAGER edit timeout: {te}")
        raise HTTPException(status_code=504, detail="GPT-IMAGER API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"GPT-IMAGER edit HTTP error: {he}")
        raise HTTPException(status_code=502, detail="GPT-IMAGER upstream error")
    except Exception as e:
        logger.error(f"GPT-IMAGER edit unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit image with GPT-IMAGER")

@router.get("/gpt-imager/edit", response_model=ImageResponse, summary="GPT-IMAGER - Edit Image (GET)")
async def gpt_imager_edit_get(
    text: str = Query(..., description="Editing instructions"),
    link: str = Query(..., description="URL of the image to edit"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for GPT-IMAGER image editing.
    Example: /api/gpt-imager/edit?text=Make+the+icon+gold&link=https://sii3.top/DarkAI.jpg&api_key=YOUR_KEY
    """
    await validate_api_key(api_key)
    
    if not link.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid image URL format - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/gpt-img.php"
    params = {"text": text, "link": link}
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            return await _get_and_parse(client, base_url, params, timeout=90.0)
    except httpx.TimeoutException as te:
        logger.error(f"GPT-IMAGER edit GET timeout: {te}")
        raise HTTPException(status_code=504, detail="GPT-IMAGER API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"GPT-IMAGER edit GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="GPT-IMAGER upstream error")
    except Exception as e:
        logger.error(f"GPT-IMAGER edit GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit image with GPT-IMAGER")

@router.post("/seedream-4/create", response_model=ImageResponse, summary="SeedReam-4 - Create Image")
async def seedream4_create_post(request: SimpleImageRequest, req: Request):
    """
    Create images using the SeedReam-4.0 model API.
    
    - **text**: Description of the image to create
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Advanced SeedReam-4.0 image generation
    - High-quality, detailed results
    - Fast processing
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/SeedReam-4.php"
    data = {"text": request.text}
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            return await _post_and_parse(client, base_url, data, timeout=120.0)
    except httpx.TimeoutException as te:
        logger.error(f"SeedReam-4 create timeout: {te}")
        raise HTTPException(status_code=504, detail="SeedReam-4 API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"SeedReam-4 create HTTP error: {he}")
        raise HTTPException(status_code=502, detail="SeedReam-4 upstream error")
    except Exception as e:
        logger.error(f"SeedReam-4 create unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create image with SeedReam-4")

@router.get("/seedream-4/create", response_model=ImageResponse, summary="SeedReam-4 - Create Image (GET)")
async def seedream4_create_get(
    text: str = Query(..., description="Description of the image to create"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for SeedReam-4 image creation.
    Example: /api/seedream-4/create?text=Billie_Eilish&api_key=YOUR_KEY
    """
    await validate_api_key(api_key)
    base_url = "https://sii3.top/api/SeedReam-4.php"
    params = {"text": text}
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            return await _get_and_parse(client, base_url, params, timeout=120.0)
    except httpx.TimeoutException as te:
        logger.error(f"SeedReam-4 create GET timeout: {te}")
        raise HTTPException(status_code=504, detail="SeedReam-4 API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"SeedReam-4 create GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="SeedReam-4 upstream error")
    except Exception as e:
        logger.error(f"SeedReam-4 create GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create image with SeedReam-4")

@router.post("/seedream-4/edit", response_model=ImageResponse, summary="SeedReam-4 - Edit Images (Up to 4)")
async def seedream4_edit_post(request: SeedReam4Request, req: Request):
    """
    Edit up to 4 images using the SeedReam-4.0 model API.
    
    - **text**: Editing instructions (e.g., "Merge the photos", "Make more cinematic with neon lights")
    - **links**: Comma-separated image URLs (max 4)
    - **api_key**: Your DarkAI API key (required)
    
    Features:
    - Edit up to 4 images in one request
    - Advanced image merging and modification
    - Cinematic effects and enhancements
    """
    await validate_api_key(request.api_key)
    
    if not request.links or not request.links.strip():
        raise HTTPException(status_code=400, detail="Image links are required for editing")
    
    # Parse and validate links
    links_list = [l.strip() for l in request.links.split(",") if l.strip()]
    
    if not links_list:
        raise HTTPException(status_code=400, detail="At least one valid image link is required for editing")
    if len(links_list) > 4:
        raise HTTPException(status_code=400, detail="Maximum of 4 images supported for editing")
    
    # Validate each URL format
    for link in links_list:
        if not link.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail=f"Invalid URL format: {link} - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/SeedReam-4.php"
    data = {"text": request.text, "links": ",".join(links_list)}
    
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            return await _post_and_parse(client, base_url, data, timeout=150.0)
    except httpx.TimeoutException as te:
        logger.error(f"SeedReam-4 edit timeout: {te}")
        raise HTTPException(status_code=504, detail="SeedReam-4 API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"SeedReam-4 edit HTTP error: {he}")
        raise HTTPException(status_code=502, detail="SeedReam-4 upstream error")
    except Exception as e:
        logger.error(f"SeedReam-4 edit unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit images with SeedReam-4")

@router.get("/seedream-4/edit", response_model=ImageResponse, summary="SeedReam-4 - Edit Images (GET)")
async def seedream4_edit_get(
    text: str = Query(..., description="Editing instructions"),
    links: str = Query(..., description="Comma-separated image URLs (max 4)"),
    api_key: str = Query(..., description="API key for authentication"),
    req: Request = None
):
    """
    GET endpoint for SeedReam-4 image editing.
    Example: /api/seedream-4/edit?text=Merge+the+photos&links=link1,link2,link3&api_key=YOUR_KEY
    """
    await validate_api_key(api_key)
    
    if not links or not links.strip():
        raise HTTPException(status_code=400, detail="Image links are required for editing")
    
    # Parse and validate links
    links_list = [l.strip() for l in links.split(",") if l.strip()]
    
    if not links_list:
        raise HTTPException(status_code=400, detail="At least one valid image link is required for editing")
    if len(links_list) > 4:
        raise HTTPException(status_code=400, detail="Maximum of 4 images supported for editing")
    
    # Validate each URL format
    for link in links_list:
        if not link.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail=f"Invalid URL format: {link} - must start with http:// or https://")
    
    base_url = "https://sii3.top/api/SeedReam-4.php"
    params = {"text": text, "links": ",".join(links_list)}
    
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            return await _get_and_parse(client, base_url, params, timeout=150.0)
    except httpx.TimeoutException as te:
        logger.error(f"SeedReam-4 edit GET timeout: {te}")
        raise HTTPException(status_code=504, detail="SeedReam-4 API timed out")
    except httpx.HTTPStatusError as he:
        logger.error(f"SeedReam-4 edit GET HTTP error: {he}")
        raise HTTPException(status_code=502, detail="SeedReam-4 upstream error")
    except Exception as e:
        logger.error(f"SeedReam-4 edit GET unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit images with SeedReam-4")

# --- Original Nano Banana Function -----------------------------------------

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
