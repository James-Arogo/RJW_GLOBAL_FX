"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.core.config import settings
from app.schemas.user import (
    UserCreate,
    LoginRequest,
    PasswordChangeRequest,
    UserResponse,
    TokenResponse,
    MeResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user):
    """Convert User model to UserResponse."""
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        balance_kes=float(user.balance_kes),
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    Creates account with hashed password (bcrypt) and 10,000 KES virtual balance.
    """
    
    existing_user = await UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await UserService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await UserService.create_user(db, user_data)
    
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data=token_data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_response(user),
        "disclaimer": settings.SIMULATION_DISCLAIMER
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login user.
    
    Returns access token + refresh token on successful authentication.
    """
    
    user = await UserService.authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data=token_data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_response(user),
        "disclaimer": settings.SIMULATION_DISCLAIMER
    }


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user info.
    
    Protected endpoint - requires valid JWT access token.
    Returns user profile including current balance.
    """
    
    user = await UserService.get_user_by_id(db, current_user["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user": _user_response(user),
        "disclaimer": settings.SIMULATION_DISCLAIMER
    }


@router.put("/me", response_model=MeResponse)
async def update_me(
    profile_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update the current user's profile details."""
    user = await UserService.get_user_by_id(db, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        user = await UserService.update_user_profile(db, user, profile_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {
        "user": _user_response(user),
        "disclaimer": settings.SIMULATION_DISCLAIMER
    }


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change the current user's password."""
    user = await UserService.get_user_by_id(db, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    try:
        await UserService.change_password(db, user, password_data.current_password, password_data.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return {"message": "Password updated successfully", "disclaimer": settings.SIMULATION_DISCLAIMER}
