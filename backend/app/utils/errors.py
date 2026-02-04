"""
Custom Exception Classes and Error Boundaries
Enhancement #9: Structured error handling
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Union

class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class AuthenticationError(AppException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR")

class AuthorizationError(AppException):
    """User not authorized"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")

class NotFoundError(AppException):
    """Resource not found"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404, error_code="NOT_FOUND")

class ValidationException(AppException):
    """Validation error"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")

class SessionError(AppException):
    """Session related error"""
    def __init__(self, message: str = "Session error"):
        super().__init__(message, status_code=400, error_code="SESSION_ERROR")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions"""
    from app.utils.logger import logger
    logger.warning(f"AppException: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.message
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    from app.utils.logger import logger
    errors = exc.errors()
    messages = [f"{e['loc'][-1]}: {e['msg']}" for e in errors]
    logger.warning(f"Validation error: {messages}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "detail": messages[0] if len(messages) == 1 else messages
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    from app.utils.logger import logger
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred"
        }
    )
