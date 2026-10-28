"""Common schemas."""

from pydantic import BaseModel
from typing import Any, Optional


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str
    version: str
    environment: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development"
            }
        }


class MessageResponse(BaseModel):
    """Schema for message response."""
    
    message: str
    data: Optional[Any] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation successful",
                "data": None
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error response."""
    
    detail: str
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials",
                "error_code": "AUTH_001"
            }
        }
