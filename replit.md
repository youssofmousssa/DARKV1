# DarkAI Pro Backend API

## Overview

DarkAI Pro is a comprehensive AI API backend that provides access to 18+ AI models across multiple domains including text generation, image processing, voice synthesis, video creation, music generation, and social media content downloading. The system acts as a unified gateway to various external AI services while implementing enterprise-grade security, authentication, and monitoring capabilities.

The backend serves as a proxy/aggregator for multiple AI model endpoints, providing a consistent API interface for clients while handling authentication, rate limiting, request tracking, and response optimization. It supports various AI capabilities from text-to-speech, image generation and editing, video creation, background removal, music composition, and universal social media downloading.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**September 9, 2025**: Completed comprehensive backend implementation with all DarkAI API endpoints fully functional and documented in Swagger UI.

## System Architecture

### Core API Framework
- **FastAPI** application with comprehensive OpenAPI documentation
- **SQLAlchemy ORM** with declarative base for database operations
- **Async/await** patterns throughout for optimal performance
- **Pydantic models** for request/response validation and serialization

### Database Layer
- **SQLAlchemy** with flexible database URL configuration
- **SQLite** as default with easy PostgreSQL migration path
- Connection pooling with pre-ping and recycling for reliability
- Three core entities: Clients, AccessTokens, and Request tracking

### Authentication & Security Architecture
- **Multi-layered security middleware** with custom auth and security components
- **JWT-based access tokens** with rotating keys and short expiration
- **API key authentication** with hashed storage and client secret validation
- **HMAC request signing** to prevent token scraping and replay attacks
- **Request ID tracking** with nonce validation using Redis for deduplication
- **Rate limiting** per client/IP/model with Redis-backed token bucket algorithm

### External Service Integration
- **HTTP client architecture** using `httpx` with proper timeout handling
- **Model router service** that maps requests to 18+ different AI model endpoints
- **Unified response formatting** across all model types while preserving model-specific features
- **Error handling and fallback** mechanisms for external service failures

### Caching & Performance
- **Redis integration** with graceful fallback to in-memory cache when Redis unavailable
- **Response caching** for identical requests to reduce costs and latency
- **Connection pooling** and keep-alive for external API calls
- **Async processing** with proper timeout management for long-running operations

### Request Processing Pipeline
- **Security middleware** adds standard security headers and request timing
- **Authentication middleware** validates tokens, signatures, and request IDs
- **Route handlers** for each AI model category with consistent error handling
- **Response transformation** to maintain consistent API contract

### Monitoring & Logging
- **Structured logging** with file and console output
- **Request tracking** with full audit trail in database
- **Performance metrics** including latency and response size tracking
- **Security event logging** for authentication failures and suspicious activity

## External Dependencies

### AI Model Services
- **Primary AI endpoint**: `sii3.moayman.top/api/` - hosts 18+ different AI models
  - Text generation (online, standard, super_genius, gemini_pro, etc.)
  - Image generation and editing (gemini-img.php)
  - Voice synthesis with multiple voices (voice.php)
  - Video generation from text/images (veo3.php)
  - Music creation with lyrics (music.php)
  - Background removal (remove-bg.php)
  - Universal social media downloader (do.php)

### Infrastructure Dependencies
- **Redis** - for caching, rate limiting, and nonce storage with fallback support
- **Database** - SQLite default with PostgreSQL migration capability
- **HTTP client** - httpx for async external API communication

### Security & Authentication
- **JWT libraries** for token generation and validation
- **bcrypt/passlib** for password and API key hashing
- **HMAC signing** for request authentication and anti-replay protection
- **UUID generation** for request ID creation

### Development & Deployment
- **python-dotenv** for environment variable management
- **uvicorn** ASGI server for production deployment
- **CORS middleware** for cross-origin request handling
- **Trusted host middleware** for additional security hardening