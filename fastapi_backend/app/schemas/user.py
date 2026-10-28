"""User schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration."""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "student123",
                "email": "student@university.ac.ke",
                "password": "SecurePass123!"
            }
        }


class UserUpdateRequest(BaseModel):
    """Schema for profile updates."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    """Schema for password changes."""

    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """Schema for user login."""
    
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "student123",
                "password": "SecurePass123!"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response."""
    
    id: str
    username: str
    email: str
    balance_kes: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "student123",
                "email": "student@university.ac.ke",
                "balance_kes": 129500.0,
                "is_active": True,
                "created_at": "2024-01-29T12:00:00",
                "updated_at": "2024-01-29T12:00:00"
            }
        }


class TokenResponse(BaseModel):
    """Schema for token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    disclaimer: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "student123",
                    "email": "student@university.ac.ke",
                    "balance_kes": 10000.0,
                    "is_active": True,
                    "created_at": "2024-01-29T12:00:00",
                    "updated_at": "2024-01-29T12:00:00"
                },
                "disclaimer": "This is a simulated forex game for learning & fun only..."
            }
        }


class MeResponse(BaseModel):
    """Schema for /auth/me response."""
    
    user: UserResponse
    disclaimer: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "student123",
                    "email": "student@university.ac.ke",
                    "balance_kes": 10000.0,
                    "is_active": True,
                    "created_at": "2024-01-29T12:00:00",
                    "updated_at": "2024-01-29T12:00:00"
                },
                "disclaimer": "This is a simulated forex game for learning & fun only..."
            }
        }
