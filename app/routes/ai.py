from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import time
from app.utils.logging import logger

router = APIRouter()

class SimpleTextRequest(BaseModel):
    text: str
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

# AI Chat Models - Separate endpoints for each model
@router.post("/ai/online", summary="Online AI Model")
async def online_ai(request: SimpleTextRequest, req: Request):
    """
    Online AI model for text generation
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"online": request.text})
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Online AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/standard", summary="Standard AI Model")
async def standard_ai(request: SimpleTextRequest, req: Request):
    """
    Standard AI model for text generation
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"standard": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Standard AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/super-genius", summary="Super Genius AI Model")
async def super_genius_ai(request: SimpleTextRequest, req: Request):
    """
    Super Genius AI model for advanced text generation
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"super-genius": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Super Genius AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/online-genius", summary="Online Genius AI Model")
async def online_genius_ai(request: SimpleTextRequest, req: Request):
    """
    Online Genius AI model for text generation
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"online-genius": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Online Genius AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Gemini Models - Separate endpoints
@router.post("/gemini/pro", summary="Gemini 2.5 Pro")
async def gemini_pro(request: SimpleTextRequest, req: Request):
    """
    Gemini 2.5 Pro model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/gemini-dark.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"gemini-pro": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemini Pro error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini/deep", summary="Gemini 2.5 Deep Search")
async def gemini_deep(request: SimpleTextRequest, req: Request):
    """
    Gemini 2.5 Deep Search model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/gemini-dark.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"gemini-deep": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemini Deep error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini/flash", summary="Gemini 2.5 Flash")
async def gemini_flash(request: SimpleTextRequest, req: Request):
    """
    Gemini 2.5 Flash model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/DARK/gemini.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"text": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemini Flash error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Gemma Models - Separate endpoints
@router.post("/gemma/4b", summary="Gemma 4B Model")
async def gemma_4b(request: SimpleTextRequest, req: Request):
    """
    Gemma 4B model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"4b": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemma 4B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemma/12b", summary="Gemma 12B Model")
async def gemma_12b(request: SimpleTextRequest, req: Request):
    """
    Gemma 12B model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"12b": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemma 12B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemma/27b", summary="Gemma 27B Model")
async def gemma_27b(request: SimpleTextRequest, req: Request):
    """
    Gemma 27B model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"27b": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"Gemma 27B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WormGPT Model
@router.post("/wormgpt", summary="WormGPT Model")
async def wormgpt(request: SimpleTextRequest, req: Request):
    """
    WormGPT AI model
    
    - **text**: Your prompt/question
    - **api_key**: Your DarkAI API key (required)
    
    ⚠️ Disclaimer: This project is created for educational and research purposes only. 
    The user is solely responsible for how they choose to use it.
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/DARK/api/wormgpt.php"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"response": response.text}
    except Exception as e:
        logger.error(f"WormGPT error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")