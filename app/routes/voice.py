from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class SimpleVoiceRequest(BaseModel):
    text: str

class VoiceWithStyleRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    style: Optional[str] = None

class VoiceResponse(BaseModel):
    status: str
    audio_url: str
    voice_used: str
    style_used: Optional[str] = None

@router.post("/voice", response_model=VoiceResponse, summary="Text to Speech - Default Settings")
async def voice_default(request: SimpleVoiceRequest, req: Request):
    """
    Convert text to speech with default voice settings
    
    - **text**: Text to convert to speech
    
    Uses default voice and style settings for quick conversion
    """
    base_url = "https://sii3.moayman.top/api/voice.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            # Handle different response formats
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
                audio_url = result.get("url", result.get("audio_url", ""))
            else:
                audio_url = response.url if response.status_code == 200 else ""
            
            if not audio_url and response.text.startswith("http"):
                audio_url = response.text.strip()
            
            return VoiceResponse(
                status="success",
                audio_url=str(audio_url),
                voice_used="default",
                style_used=None
            )
            
    except Exception as e:
        logger.error(f"Voice API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice")

@router.post("/voice/custom", response_model=VoiceResponse, summary="Text to Speech - Custom Voice & Style")
async def voice_custom(request: VoiceWithStyleRequest, req: Request):
    """
    Convert text to speech with custom voice and style options
    
    Available voices:
    - **nova**: Nova voice
    - **alloy**: Alloy voice
    - **verse**: Verse voice
    - **flow**: Flow voice
    - **aria**: Aria voice
    - **lumen**: Lumen voice
    
    Available styles:
    - **cheerful tone**: Cheerful speaking style
    - **soft whisper**: Soft whispering style
    - Custom styles supported
    
    You can set voice, style, or both
    """
    base_url = "https://sii3.moayman.top/api/voice.php"
    
    # Validate voice options if provided
    if request.voice:
        valid_voices = ["nova", "alloy", "verse", "flow", "aria", "lumen"]
        if request.voice not in valid_voices:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid voice. Choose from: {', '.join(valid_voices)}"
            )
    
    try:
        params = {"text": request.text}
        
        if request.voice:
            params["voice"] = request.voice
        if request.style:
            params["style"] = request.style
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            # Handle different response formats
            if response.headers.get("content-type", "").startswith("application/json"):
                result = response.json()
                audio_url = result.get("url", result.get("audio_url", ""))
            else:
                audio_url = response.url if response.status_code == 200 else ""
            
            if not audio_url and response.text.startswith("http"):
                audio_url = response.text.strip()
            
            return VoiceResponse(
                status="success",
                audio_url=str(audio_url),
                voice_used=request.voice or "default",
                style_used=request.style
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Voice generation timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Voice API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Voice API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice")