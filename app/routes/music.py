from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx
from typing import Optional
from app.utils.logging import logger

router = APIRouter()

class MusicWithLyricsRequest(BaseModel):
    lyrics: str
    tags: Optional[str] = None

class SimpleTextRequest(BaseModel):
    text: str

class MusicResponse(BaseModel):
    status: str
    audio_url: str
    music_type: str
    tags_used: Optional[str] = None

@router.post("/music", response_model=MusicResponse, summary="Music Creation with Lyrics")
async def create_music_with_lyrics(request: MusicWithLyricsRequest, req: Request):
    """
    Create music with lyrics and custom style tags
    
    - **lyrics**: Song lyrics text
    - **tags**: Music style tags (optional, e.g., "sad piano hop pop")
    
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
    base_url = "https://sii3.moayman.top/api/music.php"
    
    try:
        params = {"lyrics": request.lyrics}
        if request.tags:
            params["tags"] = request.tags
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(base_url, data=params)
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            
            audio_url = result.get("url", result.get("audio_url", ""))
            if not audio_url and response.text.startswith("http"):
                audio_url = response.text.strip()
            
            return MusicResponse(
                status="success",
                audio_url=audio_url,
                music_type="with_lyrics",
                tags_used=request.tags
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Music generation timeout")
    except Exception as e:
        logger.error(f"Music API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create music")

@router.post("/create-music", response_model=MusicResponse, summary="Create 15s Instrumental Music")
async def create_instrumental_music(request: SimpleTextRequest, req: Request):
    """
    Create 15-second instrumental music without lyrics
    
    - **text**: Music description/style (e.g., "love", "dramatic", "upbeat")
    
    Creates short instrumental music clips perfect for background music
    """
    base_url = "https://sii3.moayman.top/api/create-music.php"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, data={"text": request.text})
            response.raise_for_status()
            
            result = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            
            audio_url = result.get("url", result.get("audio_url", ""))
            if not audio_url and response.text.startswith("http"):
                audio_url = response.text.strip()
            
            return MusicResponse(
                status="success",
                audio_url=audio_url,
                music_type="instrumental",
                tags_used=None
            )
            
    except Exception as e:
        logger.error(f"Instrumental music API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create instrumental music")