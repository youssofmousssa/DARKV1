import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_api_key() -> str:
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_client_secret() -> str:
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def generate_request_id() -> str:
        return str(uuid.uuid4())
    
    @staticmethod
    def verify_hmac_signature(secret: str, method: str, path: str, timestamp: str, body_hash: str, signature: str) -> bool:
        string_to_sign = f"{method}\n{path}\n{timestamp}\n{body_hash}"
        expected = hmac.new(
            secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def create_access_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())
        })
        
        return jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str, secret_key: str) -> dict:
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )