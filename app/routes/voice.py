from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class VoiceRequest(BaseModel):
    text: str
    voice: Optional[str] = "nova"  # Default voice
    style: Optional[str] = None

class VoiceResponse(BaseModel):
    status: str
    audio_url: str
    voice_used: str
    style_used: Optional[str] = None

@router.post("/voice", response_model=VoiceResponse, summary="Text to Speech Generation")
async def text_to_speech(request: VoiceRequest, req: Request):
    """
    Convert text to speech with multiple voice options
    
    Available voices:
    - **nova**: Nova voice (default)
    - **alloy**: Alloy voice
    - **verse**: Verse voice
    - **flow**: Flow voice
    - **aria**: Aria voice
    - **lumen**: Lumen voice
    
    Optional styles:
    - **cheerful tone**: Cheerful speaking style
    - **soft whisper**: Soft whispering style
    - Custom styles supported
    """
    base_url = "https://sii3.moayman.top/api/voice.php"
    
    # Validate voice options
    valid_voices = ["nova", "alloy", "verse", "flow", "aria", "lumen"]
    if request.voice not in valid_voices:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid voice. Choose from: {', '.join(valid_voices)}"
        )
    
    try:
        params = {
            "text": request.text,
            "voice": request.voice
        }
        
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
                # If response is direct audio URL or file
                audio_url = response.url if response.status_code == 200 else ""
            
            if not audio_url:
                # Sometimes the API returns the audio URL in response text
                audio_url = response.text.strip() if response.text.startswith("http") else ""
            
            return VoiceResponse(
                status="success",
                audio_url=audio_url,
                voice_used=request.voice,
                style_used=request.style
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Voice generation timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Voice API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Voice API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate voice")