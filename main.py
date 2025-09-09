from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.database import engine, Base, get_db
from app.auth.middleware import AuthMiddleware, SecurityMiddleware
from app.routes import auth, ai, image, voice, video, music, social, background
from app.utils.redis_client import redis_client
from app.utils.logging import setup_logging

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    try:
        await redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}, using in-memory fallback")
    setup_logging()
    yield
    # Shutdown
    try:
        await redis_client.close()
    except Exception:
        pass

app = FastAPI(
    title="DarkAI Pro Backend API",
    description="Comprehensive AI API Backend with 18+ models and advanced security",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_url="/openapi.json"
)

# Security Middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(AuthMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust all hosts for development
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Include all route modules
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai.router, prefix="/api", tags=["AI Models"])
app.include_router(image.router, prefix="/api", tags=["Image Generation"])
app.include_router(voice.router, prefix="/api", tags=["Voice & TTS"])
app.include_router(video.router, prefix="/api", tags=["Video Generation"])
app.include_router(music.router, prefix="/api", tags=["Music Generation"])
app.include_router(social.router, prefix="/api", tags=["Social Media"])
app.include_router(background.router, prefix="/api", tags=["Background Removal"])

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "DarkAI Pro Backend API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "auth": "/auth",
            "api": "/api"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    try:
        await redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        access_log=True,
        log_level="info"
    )