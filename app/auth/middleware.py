import time
import hashlib
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.utils.security import SecurityUtils
from app.utils.redis_client import redis_client
from app.utils.logging import logger
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        # Add processing time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.excluded_paths = ["/", "/docs", "/redoc", "/openapi.json", "/health", "/auth/register", "/auth/login"]
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip auth for excluded paths
        if any(path.startswith(excluded) for excluded in self.excluded_paths):
            return await call_next(request)
        
        # Get request ID
        request_id = request.headers.get("x-request-id")
        if not request_id:
            return JSONResponse(
                status_code=400,
                content={"error": "X-Request-ID header is required"}
            )
        
        # Check for duplicate request ID
        try:
            exists = await redis_client.setnx(f"rid:{request_id}", "1")
            if not exists:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Request ID already used (replay detected)"}
                )
            await redis_client.expire(f"rid:{request_id}", 60)
        except Exception as e:
            logger.error(f"Redis error: {e}")
        
        # Verify Authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authorization header required"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Verify JWT token
            payload = SecurityUtils.verify_token(token, SECRET_KEY)
            request.state.client_id = payload.get("sub")
            request.state.scopes = payload.get("scope", [])
            
            # Verify HMAC signature if present
            signature = request.headers.get("x-signature")
            timestamp = request.headers.get("x-timestamp")
            
            if signature and timestamp:
                # Check timestamp window (30 seconds)
                current_time = int(time.time())
                request_time = int(timestamp)
                if abs(current_time - request_time) > 30:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Request timestamp out of allowed window"}
                    )
                
                # Get client secret from database (simplified for demo)
                client_secret = "demo-secret"  # In real implementation, fetch from DB
                
                # Compute body hash
                body = await request.body()
                body_hash = hashlib.sha256(body).hexdigest()
                
                # Verify HMAC
                if not SecurityUtils.verify_hmac_signature(
                    client_secret, 
                    request.method, 
                    request.url.path, 
                    timestamp, 
                    body_hash, 
                    signature.replace("sha256=", "")
                ):
                    return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid HMAC signature"}
                    )
            
            return await call_next(request)
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        except Exception as e:
            logger.error(f"Auth middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )