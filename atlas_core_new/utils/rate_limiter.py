"""
atlas_core_new/utils/rate_limiter.py

In-memory rate limiting for FastAPI endpoints using a sliding window approach.
Thread-safe with automatic cleanup of expired entries.
"""

import time
import threading
from typing import Dict, List, Callable, Any
from fastapi import Request, HTTPException, Depends


class RateLimiter:
    """
    In-memory rate limiter using a sliding window approach.
    
    Tracks request timestamps per IP address and enforces rate limits.
    Thread-safe with automatic cleanup of old entries.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds for the rate limit
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
    
    def _cleanup_old_entries(self, ip: str, current_time: float) -> None:
        """
        Remove request timestamps older than 2x the window from memory.
        
        Args:
            ip: Client IP address
            current_time: Current timestamp
        """
        cleanup_threshold = current_time - (self.window_seconds * 2)
        if ip in self.requests:
            self.requests[ip] = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > cleanup_threshold
            ]
            # Remove IP entry if no requests left
            if not self.requests[ip]:
                del self.requests[ip]
    
    def is_allowed(self, ip: str) -> bool:
        """
        Check if a request from the given IP is allowed.
        
        Uses a sliding window: counts requests within the last window_seconds.
        
        Args:
            ip: Client IP address
            
        Returns:
            True if request is allowed, False if rate limited
        """
        with self.lock:
            current_time = time.time()
            
            # Cleanup old entries
            self._cleanup_old_entries(ip, current_time)
            
            # Calculate window start time
            window_start = current_time - self.window_seconds
            
            # Get requests within the current window
            if ip not in self.requests:
                self.requests[ip] = []
            
            # Count requests within the window
            requests_in_window = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > window_start
            ]
            
            # Check if limit exceeded
            if len(requests_in_window) >= self.max_requests:
                return False
            
            # Add current request timestamp
            self.requests[ip].append(current_time)
            return True
    
    def get_remaining(self, ip: str) -> int:
        """
        Get the number of remaining requests allowed for the IP.
        
        Args:
            ip: Client IP address
            
        Returns:
            Number of remaining requests in the current window
        """
        with self.lock:
            current_time = time.time()
            window_start = current_time - self.window_seconds
            
            if ip not in self.requests:
                return self.max_requests
            
            requests_in_window = [
                timestamp for timestamp in self.requests[ip]
                if timestamp > window_start
            ]
            
            remaining = max(0, self.max_requests - len(requests_in_window))
            return remaining
    
    def reset(self, ip: str) -> None:
        """
        Reset the rate limit for a specific IP (useful for testing).
        
        Args:
            ip: Client IP address
        """
        with self.lock:
            if ip in self.requests:
                del self.requests[ip]


# Create instances for different rate limit tiers
_rate_limiter_ai = RateLimiter(max_requests=30, window_seconds=60)  # 30 requests per minute
_rate_limiter_strict = RateLimiter(max_requests=10, window_seconds=60)  # 10 requests per minute


def _get_client_ip(request: Request) -> str:
    """
    Extract client IP from request, considering proxies.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Client IP address as string
    """
    # Check X-Forwarded-For header first (for proxied requests)
    if request.headers.get("x-forwarded-for"):
        return request.headers.get("x-forwarded-for").split(",")[0].strip()
    
    # Check X-Real-IP header
    if request.headers.get("x-real-ip"):
        return request.headers.get("x-real-ip")
    
    # Fall back to client IP from connection
    return request.client.host if request.client else "unknown"


async def rate_limit_ai(request: Request) -> None:
    """
    FastAPI dependency for AI endpoint rate limiting (30 requests/minute per IP).
    
    Usage:
        @app.post("/chat", dependencies=[Depends(rate_limit_ai)])
        async def chat(request: ChatRequest):
            ...
    
    Args:
        request: FastAPI Request object
        
    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded
    """
    ip = _get_client_ip(request)
    
    if not _rate_limiter_ai.is_allowed(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait before trying again."
        )


async def rate_limit_strict(request: Request) -> None:
    """
    FastAPI dependency for strict rate limiting (10 requests/minute per IP).
    
    Use for expensive endpoints like text-to-speech (TTS) or image generation.
    
    Usage:
        @app.post("/tts", dependencies=[Depends(rate_limit_strict)])
        async def generate_tts(request: TTSRequest):
            ...
    
    Args:
        request: FastAPI Request object
        
    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded
    """
    ip = _get_client_ip(request)
    
    if not _rate_limiter_strict.is_allowed(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait before trying again."
        )


def create_rate_limiter(max_requests: int, window_seconds: int) -> Callable:
    """
    Create a custom rate limiter dependency.
    
    Useful for creating specialized rate limits for specific endpoints.
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds
        
    Returns:
        FastAPI dependency function
        
    Example:
        rate_limit_custom = create_rate_limiter(max_requests=5, window_seconds=60)
        
        @app.post("/expensive", dependencies=[Depends(rate_limit_custom)])
        async def expensive_operation():
            ...
    """
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    
    async def _rate_limit_dependency(request: Request) -> None:
        ip = _get_client_ip(request)
        
        if not limiter.is_allowed(ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait before trying again."
            )
    
    return _rate_limit_dependency


# Export the main components
__all__ = [
    "RateLimiter",
    "rate_limit_ai",
    "rate_limit_strict",
    "create_rate_limiter",
]
