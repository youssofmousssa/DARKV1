from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class MusicWithLyricsRequest(BaseModel):
    lyrics: str
    tags: Optional[str] = None
    api_key: str

class SimpleTextRequest(BaseModel):
    text: str
    api_key: str

# Helper function to validate API key
async def validate_api_key(api_key: str) -> bool:
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    return True

@router.post("/music", summary="Music Creation with Lyrics")
async def create_music_with_lyrics(request: MusicWithLyricsRequest, req: Request):
    """
    Create music with lyrics and custom style tags
    
    - **lyrics**: Song lyrics text
    - **tags**: Music style tags (optional, e.g., "sad piano hop pop")
    - **api_key**: Your DarkAI API key (required)
    
    Available tags include:
    epic, orchestra, cinematic, emotional, piano, sad, dramatic, hope, electronic,
    ambient, dark, powerful, pop, hiphop, future, bass, trap, lofi, rock, guitar,
    melancholy, uplifting, chill, deep, house, edm, techno, synthwave, retro,
    classical, violin, instrumental, acoustic, melodic, harmonic, dreamy, romantic,
    intense, soft, hardstyle, progressive, vocal, beats, rap, freestyle, club,
    party, funk, groove, metal, jazz, blues, soul, indie, alternative, folk,
    ballad, anthemic, minimal, industrial, world, afrobeat, latin, reggaeton,
    dancehall, oriental, arabic, ethnic, tribal, drums, percussion, strings,
    choir, opera, symphonic, modern, experimental, psytrance, chillwave,
    downtempo, relaxing, meditation, zen, trance, hardcore, dnb, breakbeat,
    glitch, future_garage, electro, urban, dreamwave
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/music.php"
    
    try:
        params = {"lyrics": request.lyrics}
        if request.tags:
            params["tags"] = request.tags
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            # Return the raw response from DarkAI API
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"audio_url": response.text.strip()}
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Music generation timeout")
    except Exception as e:
        logger.error(f"Music API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create music")

@router.post("/create-music", summary="Create 15s Instrumental Music")
async def create_instrumental_music(request: SimpleTextRequest, req: Request):
    """
    Create 15-second instrumental music without lyrics
    
    - **text**: Music description/style (e.g., "love", "dramatic", "upbeat")
    - **api_key**: Your DarkAI API key (required)
    
    Creates short instrumental music clips perfect for background music
    """
    await validate_api_key(request.api_key)
    base_url = "https://sii3.moayman.top/api/create-music.php"
    
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
        logger.error(f"Instrumental music API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create instrumental music")