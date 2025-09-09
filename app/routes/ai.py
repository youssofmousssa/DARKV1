from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import time
from app.utils.logging import logger

router = APIRouter()

class SimpleTextRequest(BaseModel):
    text: str

class AIResponse(BaseModel):
    status: str
    response: str
    model_used: str
    processing_time: float

# AI Chat Models - Separate endpoints for each model
@router.post("/ai/online", response_model=AIResponse, summary="Online AI Model")
async def online_ai(request: SimpleTextRequest, req: Request):
    """Online AI model for text generation"""
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"online": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="online",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Online AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/standard", response_model=AIResponse, summary="Standard AI Model")
async def standard_ai(request: SimpleTextRequest, req: Request):
    """Standard AI model for text generation"""
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"standard": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="standard",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Standard AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/super-genius", response_model=AIResponse, summary="Super Genius AI Model")
async def super_genius_ai(request: SimpleTextRequest, req: Request):
    """Super Genius AI model for advanced text generation"""
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"super-genius": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="super-genius",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Super Genius AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ai/online-genius", response_model=AIResponse, summary="Online Genius AI Model")
async def online_genius_ai(request: SimpleTextRequest, req: Request):
    """Online Genius AI model for text generation"""
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"online-genius": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="online-genius",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Online Genius AI error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Gemini Models - Separate endpoints
@router.post("/gemini/pro", response_model=AIResponse, summary="Gemini 2.5 Pro")
async def gemini_pro(request: SimpleTextRequest, req: Request):
    """Gemini 2.5 Pro model"""
    base_url = "https://sii3.moayman.top/api/gemini-dark.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"gemini-pro": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemini-2.5-pro",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemini Pro error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini/deep", response_model=AIResponse, summary="Gemini 2.5 Deep Search")
async def gemini_deep(request: SimpleTextRequest, req: Request):
    """Gemini 2.5 Deep Search model"""
    base_url = "https://sii3.moayman.top/api/gemini-dark.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"gemini-deep": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemini-2.5-deep",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemini Deep error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini/flash", response_model=AIResponse, summary="Gemini 2.5 Flash")
async def gemini_flash(request: SimpleTextRequest, req: Request):
    """Gemini 2.5 Flash model"""
    base_url = "https://sii3.moayman.top/DARK/gemini.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, json={"text": request.text}, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemini-2.5-flash",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemini Flash error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Gemma Models - Separate endpoints
@router.post("/gemma/4b", response_model=AIResponse, summary="Gemma 4B Model")
async def gemma_4b(request: SimpleTextRequest, req: Request):
    """Gemma 4B model"""
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"4b": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemma-4b",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemma 4B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemma/12b", response_model=AIResponse, summary="Gemma 12B Model")
async def gemma_12b(request: SimpleTextRequest, req: Request):
    """Gemma 12B model"""
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"12b": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemma-12b",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemma 12B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemma/27b", response_model=AIResponse, summary="Gemma 27B Model")
async def gemma_27b(request: SimpleTextRequest, req: Request):
    """Gemma 27B model"""
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"27b": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="gemma-27b",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"Gemma 27B error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WormGPT Model
@router.post("/wormgpt", response_model=AIResponse, summary="WormGPT Model")
async def wormgpt(request: SimpleTextRequest, req: Request):
    """
    WormGPT AI model
    
    ⚠️ Disclaimer: This project is created for educational and research purposes only. 
    The user is solely responsible for how they choose to use it.
    """
    base_url = "https://sii3.moayman.top/DARK/api/wormgpt.php"
    
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="wormgpt",
                processing_time=time.time() - start_time
            )
    except Exception as e:
        logger.error(f"WormGPT error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")