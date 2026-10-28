"""User service for user management."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models import User
from app.schemas.user import UserCreate, UserUpdateRequest
from app.core.security import hash_password, verify_password


class UserService:
    """Service for user operations."""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            username=user_data.username.strip(),
            email=user_data.email.strip().lower(),
            password_hash=hash_password(user_data.password),
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        """Get user by username."""
        normalized_username = username.strip().lower()
        result = await db.execute(
            select(User).where(func.lower(User.username) == normalized_username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        normalized_email = email.strip().lower()
        result = await db.execute(
            select(User).where(func.lower(User.email) == normalized_email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        """Get user by ID."""
        normalized_user_id = user_id
        if isinstance(user_id, str):
            try:
                normalized_user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        result = await db.execute(select(User).where(User.id == normalized_user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        """Authenticate user with username or email and password."""
        identifier = username.strip()
        user = await UserService.get_user_by_email(db, identifier) if "@" in identifier else None
        if not user:
            user = await UserService.get_user_by_username(db, identifier)
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def update_user_balance(db: AsyncSession, user_id: str, amount: float) -> User:
        """Update user balance."""
        user = await UserService.get_user_by_id(db, user_id)
        
        if user:
            user.balance += amount
            await db.commit()
            await db.refresh(user)
        
        return user

    @staticmethod
    async def update_user_profile(db: AsyncSession, user: User, profile_data: UserUpdateRequest) -> User:
        """Update username and email after uniqueness checks."""
        normalized_username = profile_data.username.strip()
        normalized_email = profile_data.email.strip().lower()

        existing_user = await UserService.get_user_by_username(db, normalized_username)
        if existing_user and existing_user.id != user.id:
            raise ValueError("Username already registered")

        existing_email = await UserService.get_user_by_email(db, normalized_email)
        if existing_email and existing_email.id != user.id:
            raise ValueError("Email already registered")

        user.username = normalized_username
        user.email = normalized_email
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(db: AsyncSession, user: User, current_password: str, new_password: str) -> User:
        """Change a user's password after verifying the current one."""
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        await db.commit()
        await db.refresh(user)
        return user
