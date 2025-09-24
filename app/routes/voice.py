from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class SimpleVoiceRequest(BaseModel):
    text: str
    api_key: str

class VoiceWithStyleRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    style: Optional[str] = None
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

@router.post("/voice", summary="Text to Speech - Default Settings")
async def voice_default(request: SimpleVoiceRequest, req: Request):
    """
    Convert text to speech with default voice settings
    
    - **text**: Text to convert to speech
    - **api_key**: Your DarkAI API key (required)
    
    Uses default voice and style settings for quick conversion
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/voice.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"audio_url": response.text.strip()}
            
    except Exception as e:
        logger.error(f"Voice API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice")

@router.post("/voice/custom", summary="Text to Speech - Custom Voice & Style")
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
    - **api_key**: Your DarkAI API key (required)
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.top/api/voice.php"
    
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
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"audio_url": response.text.strip()}
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Voice generation timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Voice API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Voice API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice")
