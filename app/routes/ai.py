from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional, Dict, Any
from app.utils.logging import logger

router = APIRouter()

class AIRequest(BaseModel):
    online: Optional[str] = None
    standard: Optional[str] = None
    super_genius: Optional[str] = None
    online_genius: Optional[str] = None
    gemini_pro: Optional[str] = None
    gemini_deep: Optional[str] = None
    text: Optional[str] = None
    model_27b: Optional[str] = None
    model_12b: Optional[str] = None
    model_4b: Optional[str] = None

class AIResponse(BaseModel):
    status: str
    response: str
    model_used: str
    processing_time: float

@router.post("/ai", response_model=AIResponse, summary="Multi-Model AI Chat")
async def ai_chat(request: AIRequest, req: Request):
    """
    Connect to multiple AI models for text generation
    
    Available models:
    - **online**: Online AI model
    - **standard**: Standard AI model  
    - **super_genius**: Super Genius AI model
    - **online_genius**: Online Genius AI model
    """
    base_url = "https://sii3.moayman.top/api/ai.php"
    
    # Determine which model to use
    model_data = {}
    model_used = "unknown"
    
    if request.online:
        model_data["online"] = request.online
        model_used = "online"
    elif request.standard:
        model_data["standard"] = request.standard
        model_used = "standard"
    elif request.super_genius:
        model_data["super-genius"] = request.super_genius
        model_used = "super-genius"
    elif request.online_genius:
        model_data["online-genius"] = request.online_genius
        model_used = "online-genius"
    else:
        raise HTTPException(status_code=400, detail="Please provide a query for one of the available models")
    
    try:
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data=model_data)
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used=model_used,
                processing_time=processing_time
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"API error: {e.response.text}")
    except Exception as e:
        logger.error(f"AI API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemini-dark", response_model=AIResponse, summary="Gemini AI Models")
async def gemini_ai(request: AIRequest, req: Request):
    """
    Access Gemini AI models
    
    Available models:
    - **gemini_pro**: Gemini 2.5 Pro
    - **gemini_deep**: Gemini 2.5 Deep Search
    - **text**: Gemini 2.5 Flash
    """
    base_url = "https://sii3.moayman.top/api/gemini-dark.php"
    
    model_data = {}
    model_used = "unknown"
    
    if request.gemini_pro:
        model_data["gemini-pro"] = request.gemini_pro
        model_used = "gemini-2.5-pro"
    elif request.gemini_deep:
        model_data["gemini-deep"] = request.gemini_deep  
        model_used = "gemini-2.5-deep"
    elif request.text:
        # For flash model, use different endpoint
        base_url = "https://sii3.moayman.top/DARK/gemini.php"
        model_data["text"] = request.text
        model_used = "gemini-2.5-flash"
    else:
        raise HTTPException(status_code=400, detail="Please provide input for one of the Gemini models")
    
    try:
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if request.text and "DARK/gemini.php" in base_url:
                response = await client.post(base_url, json=model_data, headers={"Content-Type": "application/json"})
            else:
                response = await client.post(base_url, json=model_data, headers={"Content-Type": "application/json"})
            
            response.raise_for_status()
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used=model_used,
                processing_time=processing_time
            )
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/gemma", response_model=AIResponse, summary="Gemma AI Models")
async def gemma_ai(request: AIRequest, req: Request):
    """
    Access Gemma AI models
    
    Available models:
    - **model_4b**: Gemma 4B model
    - **model_12b**: Gemma 12B model  
    - **model_27b**: Gemma 27B model
    """
    base_url = "https://sii3.moayman.top/api/gemma.php"
    
    model_data = {}
    model_used = "unknown"
    
    if request.model_4b:
        model_data["4b"] = request.model_4b
        model_used = "gemma-4b"
    elif request.model_12b:
        model_data["12b"] = request.model_12b
        model_used = "gemma-12b"
    elif request.model_27b:
        model_data["27b"] = request.model_27b
        model_used = "gemma-27b"
    else:
        raise HTTPException(status_code=400, detail="Please provide input for one of the Gemma models")
    
    try:
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data=model_data)
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                status="success", 
                response=result.get("response", response.text),
                model_used=model_used,
                processing_time=processing_time
            )
            
    except Exception as e:
        logger.error(f"Gemma API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/wormgpt", response_model=AIResponse, summary="WormGPT AI Model")
async def wormgpt_ai(request: AIRequest, req: Request):
    """
    Access WormGPT AI model
    
    - **text**: Input text for WormGPT
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text input is required")
    
    base_url = "https://sii3.moayman.top/DARK/api/wormgpt.php"
    
    try:
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"response": response.text}
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                status="success",
                response=result.get("response", response.text),
                model_used="wormgpt",
                processing_time=processing_time
            )
            
    except Exception as e:
        logger.error(f"WormGPT API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")