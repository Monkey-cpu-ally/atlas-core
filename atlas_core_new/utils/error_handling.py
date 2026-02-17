"""
atlas_core_new/utils/error_handling.py

Centralized error handling for the FastAPI app.
"""

import re
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AtlasError(Exception):
    """Custom exception class for Atlas application errors."""
    
    def __init__(self, message: str, status_code: int = 400, detail: Optional[str] = None):
        """
        Initialize AtlasError.
        
        Args:
            message: User-facing error message
            status_code: HTTP status code (default 400)
            detail: Internal logging detail (optional)
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


def sanitize_error(exc: Exception) -> str:
    """
    Sanitize an exception to return a safe user-facing message.
    
    Strips:
    - File paths and absolute paths
    - Database connection strings
    - API keys and secrets
    - Raw tracebacks and internal details
    
    Args:
        exc: The exception to sanitize
        
    Returns:
        A safe, user-facing error message
    """
    error_str = str(exc)
    
    # Log the real error internally
    print(f"[ERROR LOGGED] {type(exc).__name__}: {error_str}")
    
    # Strip file paths (both Unix and Windows)
    sanitized = re.sub(r'[/\\](?:[^/\\]+[/\\])*[^/\\\s:]+\.py(?::\d+)?', '<file>', error_str)
    
    # Strip common connection strings and database URLs
    sanitized = re.sub(r'postgresql://[^\s]+', '<database>', sanitized)
    sanitized = re.sub(r'mysql://[^\s]+', '<database>', sanitized)
    sanitized = re.sub(r'mongodb://[^\s]+', '<database>', sanitized)
    sanitized = re.sub(r'sqlite:///[^\s]+', '<database>', sanitized)
    
    # Strip API keys and tokens
    sanitized = re.sub(r'(?:api[_-]?key|token|secret|password)["\']?\s*[:=]\s*["\']?[^\s"\']+', '<redacted>', sanitized, flags=re.IGNORECASE)
    
    # Strip environment variables and credentials
    sanitized = re.sub(r'(?:Bearer|Basic)\s+[^\s]+', '<redacted>', sanitized)
    
    # Strip traceback-like patterns
    sanitized = re.sub(r'Traceback.*?(?=\n|$)', '<traceback>', sanitized, flags=re.DOTALL)
    
    # If after sanitization the message is empty or too generic, return a default
    if not sanitized.strip() or sanitized.strip() == error_str.replace(error_str, ''):
        return "An error occurred while processing your request."
    
    return sanitized.strip()


def register_error_handlers(app: FastAPI) -> None:
    """
    Register error handlers for the FastAPI app.
    
    Handles:
    - AtlasError: Returns JSON with custom status code
    - RequestValidationError: Returns 422 with readable validation message
    - Generic Exception: Returns 500 with sanitized message
    
    Args:
        app: The FastAPI application instance
    """
    
    @app.exception_handler(AtlasError)
    async def atlas_error_handler(request: Request, exc: AtlasError):
        """Handle custom AtlasError exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors with readable messages."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"][1:])
            msg = error["msg"]
            errors.append({"field": field, "message": msg})
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Request validation failed",
                "errors": errors
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle generic exceptions with sanitized messages."""
        sanitized_msg = sanitize_error(exc)
        
        return JSONResponse(
            status_code=500,
            content={"detail": sanitized_msg}
        )


def not_found(msg: str) -> None:
    """
    Raise AtlasError with 404 status code.
    
    Args:
        msg: User-facing error message
        
    Raises:
        AtlasError: With status code 404
    """
    raise AtlasError(msg, status_code=404)


def bad_request(msg: str) -> None:
    """
    Raise AtlasError with 400 status code.
    
    Args:
        msg: User-facing error message
        
    Raises:
        AtlasError: With status code 400
    """
    raise AtlasError(msg, status_code=400)


def service_unavailable(msg: str) -> None:
    """
    Raise AtlasError with 503 status code.
    
    Args:
        msg: User-facing error message
        
    Raises:
        AtlasError: With status code 503
    """
    raise AtlasError(msg, status_code=503)


def ai_not_configured() -> None:
    """
    Raise AtlasError for unconfigured AI services.
    
    Raises:
        AtlasError: With status code 503 and standard AI offline message
    """
    raise AtlasError(
        "AI services are currently offline. Please try again later.",
        status_code=503,
        detail="OpenAI or other AI service not configured"
    )
