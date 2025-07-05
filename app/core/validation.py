"""
Input validation utilities for the CAG System.
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class URLValidator:
    """Comprehensive URL validation to prevent security issues."""
    
    # Blocked domains and patterns
    BLOCKED_DOMAINS = {
        'localhost', '127.0.0.1', '0.0.0.0', '::1',
        'metadata.google.internal',  # GCP metadata
        '169.254.169.254',  # AWS metadata
        'metadata.azure.com'  # Azure metadata
    }
    
    # Private IP ranges (CIDR notation)
    PRIVATE_IP_PATTERNS = [
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
        r'^192\.168\.',
        r'^127\.',
        r'^169\.254\.',  # Link-local
        r'^::1$',  # IPv6 localhost
        r'^fc00:',  # IPv6 private
        r'^fe80:',  # IPv6 link-local
    ]
    
    @classmethod
    def validate_url(cls, url: str) -> tuple[bool, Optional[str]]:
        """
        Validate URL for security and format.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"
        
        # Basic length check
        if len(url) > 2048:
            return False, "URL too long (max 2048 characters)"
        
        try:
            parsed = urlparse(url.strip())
        except Exception as e:
            logger.warning(f"URL parsing failed: {e}")
            return False, "Invalid URL format"
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS URLs are allowed"
        
        # Check hostname
        hostname = parsed.hostname
        if not hostname:
            return False, "URL must have a valid hostname"
        
        hostname = hostname.lower()
        
        # Check blocked domains
        if hostname in cls.BLOCKED_DOMAINS:
            logger.warning(f"Blocked domain attempted: {hostname}")
            return False, "Access to this domain is not allowed"
        
        # Check private IP ranges
        for pattern in cls.PRIVATE_IP_PATTERNS:
            if re.match(pattern, hostname):
                logger.warning(f"Private IP attempted: {hostname}")
                return False, "Access to private IP addresses is not allowed"
        
        # Check for suspicious patterns
        if any(suspicious in hostname for suspicious in ['admin', 'internal', 'private']):
            logger.warning(f"Suspicious hostname: {hostname}")
            return False, "Suspicious hostname detected"
        
        return True, None


class TextValidator:
    """Text input validation utilities."""
    
    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
        """Validate user prompt input."""
        if not prompt or not isinstance(prompt, str):
            return False, "Prompt must be a non-empty string"
        
        prompt = prompt.strip()
        
        if len(prompt) < 3:
            return False, "Prompt must be at least 3 characters long"
        
        if len(prompt) > 10000:
            return False, "Prompt too long (max 10000 characters)"
        
        # Check for potential injection attempts
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
        ]
        
        prompt_lower = prompt.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, prompt_lower):
                logger.warning(f"Suspicious prompt pattern detected: {pattern}")
                return False, "Prompt contains potentially unsafe content"
        
        return True, None
    
    @staticmethod
    def validate_user_id(user_id: str) -> tuple[bool, Optional[str]]:
        """Validate user ID format."""
        if not user_id or not isinstance(user_id, str):
            return False, "User ID must be a non-empty string"
        
        user_id = user_id.strip()
        
        if len(user_id) < 1:
            return False, "User ID cannot be empty"
        
        if len(user_id) > 100:
            return False, "User ID too long (max 100 characters)"
        
        # Allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return False, "User ID can only contain letters, numbers, hyphens, and underscores"
        
        return True, None


# Pydantic models with validation
class ValidatedCrawlRequest(BaseModel):
    url: str
    use_cache: bool = True
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        is_valid, error = URLValidator.validate_url(v)
        if not is_valid:
            raise ValueError(error)
        return v


class ValidatedGenerateRequest(BaseModel):
    prompt: str
    use_cache: bool = True
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        is_valid, error = TextValidator.validate_prompt(v)
        if not is_valid:
            raise ValueError(error)
        return v


class ValidatedCAGRequest(BaseModel):
    url: str
    query: str
    user_id: Optional[str] = None
    use_cache: bool = True
    include_history: bool = False
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        is_valid, error = URLValidator.validate_url(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        is_valid, error = TextValidator.validate_prompt(v)
        if not is_valid:
            raise ValueError(error)
        return v
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v):
        if v is not None:
            is_valid, error = TextValidator.validate_user_id(v)
            if not is_valid:
                raise ValueError(error)
        return v