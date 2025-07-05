from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import endpoints
from app.api import admin
from app.core.config import load_env, get_settings
from app.core.logging_config import setup_logging
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware
from app.services.llm_provider import configure_genai
import logging

# Load environment and configure services
load_env()
settings = get_settings()

# Setup logging
setup_logging(debug=settings.debug)
logger = logging.getLogger("app.main")

# Configure AI services
configure_genai(settings)
logger.info("AI services configured successfully")

# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=== CAG System Starting Up ===")
    logger.info(f"Application: {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Redis URL: {settings.redis_url}")
    logger.info("=== Startup Complete ===")
    
    yield
    
    # Shutdown
    logger.info("=== CAG System Shutting Down ===")
    logger.info("Cleanup completed successfully")
    logger.info("=== Shutdown Complete ===")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cache-Augmented Generation System with intelligent web content analysis",
    debug=settings.debug,
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    calls_per_minute=30,  # General rate limit
    expensive_calls_per_minute=5  # Limit for expensive endpoints
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, tags=["CAG System"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])

logger.info(f"FastAPI application '{settings.app_name}' v{settings.app_version} initialized")

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    import time
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time(),
        "environment": "development" if settings.debug else "production"
    }

