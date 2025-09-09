from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import httpx
from app.utils.logging import logger

router = APIRouter()

# Request body for lyrics-based music
class MusicWithLyricsRequest(BaseModel):
    lyrics: str
    tags: Optional[str] = None
    api_key: str

# Request body for instrumental (short music)
class SimpleTextRequest(BaseModel):
    text: str
    api_key: str

# Helper: Validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

# ✅ FULL SONG GENERATION (LYRICS + TAGS)
@router.post("/music", summary="Music Creation with Lyrics")
async def create_music_with_lyrics(request: MusicWithLyricsRequest, req: Request):
    await validate_api_key(request.api_key)

    base_url = "https://sii3.moayman.top/api/music.php"

    # Build the POST form data correctly
    form_data = {
        "lyrics": request.lyrics
    }
    if request.tags:
        form_data["tags"] = request.tags

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(base_url, data=form_data)
            response.raise_for_status()

            # If it's JSON, return parsed response
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()

            # If it's plain text (fallback)
            return {"audio_url": response.text.strip()}

    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Music generation timed out")
    except Exception as e:
        logger.error(f"[DarkAI] Music error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create music with lyrics")

# ✅ 15s INSTRUMENTAL MUSIC
@router.post("/create-music", summary="Create 15s Instrumental Music")
async def create_instrumental_music(request: SimpleTextRequest, req: Request):
    await validate_api_key(request.api_key)

    base_url = "https://sii3.moayman.top/api/create-music.php"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()

            return {"audio_url": response.text.strip()}

    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Instrumental generation timed out")
    except Exception as e:
        logger.error(f"[DarkAI] Instrumental error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create instrumental music")