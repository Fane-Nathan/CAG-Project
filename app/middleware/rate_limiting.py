"""
Rate limiting middleware for the CAG System.
"""

import time
import logging
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse of expensive endpoints.
    """
    
    def __init__(self, app, calls_per_minute: int = 10, expensive_calls_per_minute: int = 3):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.expensive_calls_per_minute = expensive_calls_per_minute
        self.clients: Dict[str, Dict[str, list]] = {}
        
        # Define expensive endpoints that need stricter limits
        self.expensive_endpoints = {
            "/cag",
            "/crawl"
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers first (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, client_ip: str, endpoint: str) -> Tuple[bool, str]:
        """
        Check if client is rate limited.
        
        Returns:
            Tuple of (is_limited, reason)
        """
        current_time = time.time()
        
        # Initialize client tracking if not exists
        if client_ip not in self.clients:
            self.clients[client_ip] = {"general": [], "expensive": []}
        
        client_data = self.clients[client_ip]
        
        # Clean old requests (older than 1 minute)
        minute_ago = current_time - 60
        client_data["general"] = [t for t in client_data["general"] if t > minute_ago]
        client_data["expensive"] = [t for t in client_data["expensive"] if t > minute_ago]
        
        # Check expensive endpoint limits
        if endpoint in self.expensive_endpoints:
            if len(client_data["expensive"]) >= self.expensive_calls_per_minute:
                return True, f"Rate limit exceeded for expensive endpoints: {self.expensive_calls_per_minute}/minute"
            client_data["expensive"].append(current_time)
        
        # Check general limits
        if len(client_data["general"]) >= self.calls_per_minute:
            return True, f"Rate limit exceeded: {self.calls_per_minute}/minute"
        
        client_data["general"].append(current_time)
        return False, ""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        client_ip = self.get_client_ip(request)
        endpoint = request.url.path
        
        # Skip rate limiting for health checks and admin endpoints
        if endpoint.startswith(("/health", "/docs", "/openapi.json")):
            return await call_next(request)
        
        # Check rate limits
        is_limited, reason = self.is_rate_limited(client_ip, endpoint)
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}: {reason}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": reason,
                    "retry_after": 60
                }
            )
        
        # Log expensive endpoint usage
        if endpoint in self.expensive_endpoints:
            logger.info(f"Expensive endpoint accessed: {endpoint} by {client_ip}")
        
        return await call_next(request)