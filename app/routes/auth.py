from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.client import Client, AccessToken
from app.utils.security import SecurityUtils
from datetime import datetime, timedelta
import os

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")

class ClientRegister(BaseModel):
    name: str
    email: EmailStr
    scopes: list = []
    allowed_models: list = []

class ClientLogin(BaseModel):
    email: EmailStr
    api_key: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    client_id: str
    scopes: list

@router.post("/register", response_model=dict, summary="Register New Client")
async def register_client(client_data: ClientRegister, db: Session = Depends(get_db)):
    """
    Register a new client with API access
    
    - **name**: Client name
    - **email**: Client email (unique)
    - **scopes**: List of allowed scopes
    - **allowed_models**: List of models client can access
    """
    # Check if email already exists
    existing_client = db.query(Client).filter(Client.email == client_data.email).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate API key and secret
    api_key = SecurityUtils.generate_api_key()
    client_secret = SecurityUtils.generate_client_secret()
    
    # Hash the credentials
    hashed_api_key = SecurityUtils.hash_password(api_key)
    hashed_secret = SecurityUtils.hash_password(client_secret)
    
    # Create client
    client = Client(
        name=client_data.name,
        email=client_data.email,
        hashed_api_key=hashed_api_key,
        client_secret_hash=hashed_secret,
        scopes=client_data.scopes or ["basic"],
        allowed_models=client_data.allowed_models or ["all"]
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return {
        "message": "Client registered successfully",
        "client_id": client.id,
        "api_key": api_key,
        "client_secret": client_secret,
        "warning": "Store these credentials securely - they will not be shown again"
    }

@router.post("/login", response_model=TokenResponse, summary="Client Login")
async def login_client(login_data: ClientLogin, db: Session = Depends(get_db)):
    """
    Authenticate client and get access token
    
    - **email**: Client email
    - **api_key**: Client API key
    """
    # Find client by email
    client = db.query(Client).filter(Client.email == login_data.email).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify API key
    if not SecurityUtils.verify_password(login_data.api_key, client.hashed_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check client status
    if client.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client account is not active"
        )
    
    # Create access token
    token_data = {
        "sub": str(client.id),
        "email": client.email,
        "scope": client.scopes,
        "models": client.allowed_models
    }
    
    expires_delta = timedelta(hours=1)
    access_token = SecurityUtils.create_access_token(
        data=token_data,
        secret_key=SECRET_KEY,
        expires_delta=expires_delta
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        client_id=str(client.id),
        scopes=client.scopes
    )

@router.get("/profile", summary="Get Client Profile")
async def get_profile(token: str = Depends(security), db: Session = Depends(get_db)):
    """Get authenticated client profile"""
    try:
        payload = SecurityUtils.verify_token(token.credentials, SECRET_KEY)
        client_id = payload.get("sub")
        
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "scopes": client.scopes,
            "allowed_models": client.allowed_models,
            "rate_limit_profile": client.rate_limit_profile,
            "status": client.status,
            "created_at": client.created_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )