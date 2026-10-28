"""
Input Validators and Decorator Factory
Provides reusable validation decorators for route handlers
"""
from functools import wraps
from flask import request
from utils.api_response import ResponseHandler
from utils.error_handler import ValidationError, InvalidPairError
from typing import Callable, Dict, Any, Optional


class ValidatorFactory:
    """Factory for creating validation decorators."""
    
    # Supported currency pairs
    SUPPORTED_PAIRS = [
        "EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD",
        "USD/CHF", "AUD/USD", "NZD/USD", "USD/CAD"
    ]
    
    # Trading constraints
    MIN_TRADE_AMOUNT = 0.01
    MAX_TRADE_AMOUNT = 10000000
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    
    @staticmethod
    def validate_pair(pairs: list = None) -> Callable:
        """
        Validates that provided currency pair(s) are supported.
        
        Args:
            pairs: List of valid pairs. If None, uses SUPPORTED_PAIRS.
        """
        valid_pairs = pairs or ValidatorFactory.SUPPORTED_PAIRS
        
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                pair = data.get('pair')
                
                if not pair:
                    raise ValidationError(
                        "Currency pair is required",
                        field='pair'
                    )
                
                if pair not in valid_pairs:
                    raise InvalidPairError(pair, valid_pairs)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_amount() -> Callable:
        """Validates that trade amount is within acceptable range."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                amount = data.get('amount')
                
                if amount is None:
                    raise ValidationError(
                        "Amount is required",
                        field='amount'
                    )
                
                try:
                    amount = float(amount)
                except (TypeError, ValueError):
                    raise ValidationError(
                        "Amount must be a valid number",
                        field='amount'
                    )
                
                if amount < ValidatorFactory.MIN_TRADE_AMOUNT:
                    raise ValidationError(
                        f"Amount must be at least {ValidatorFactory.MIN_TRADE_AMOUNT}",
                        field='amount',
                        details={'min': ValidatorFactory.MIN_TRADE_AMOUNT}
                    )
                
                if amount > ValidatorFactory.MAX_TRADE_AMOUNT:
                    raise ValidationError(
                        f"Amount exceeds maximum of {ValidatorFactory.MAX_TRADE_AMOUNT}",
                        field='amount',
                        details={'max': ValidatorFactory.MAX_TRADE_AMOUNT}
                    )
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_user_exists() -> Callable:
        """Validates that a user exists in the database."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                from models import db, User
                from flask_jwt_extended import get_jwt_identity
                
                try:
                    username = get_jwt_identity()
                except:
                    raise ValidationError("User identification failed")
                
                user = User.query.filter_by(username=username).first()
                if not user:
                    raise ValidationError("User not found")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_json(*required_fields) -> Callable:
        """
        Validates that request contains JSON with required fields.
        
        Args:
            required_fields: Names of required JSON fields
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not request.is_json:
                    raise ValidationError("Request must be JSON")
                
                data = request.get_json() or {}
                
                missing_fields = [
                    field for field in required_fields
                    if field not in data or data[field] is None
                ]
                
                if missing_fields:
                    raise ValidationError(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        details={'missing_fields': missing_fields}
                    )
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_email(field='email') -> Callable:
        """Validates email format."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                email = data.get(field, '').strip()
                
                if not email:
                    raise ValidationError("Email is required", field=field)
                
                # Simple email validation
                if '@' not in email or '.' not in email.split('@')[1]:
                    raise ValidationError("Invalid email format", field=field)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_password(min_length=8) -> Callable:
        """Validates password strength."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                password = data.get('password', '')
                
                errors = []
                
                if len(password) < min_length:
                    errors.append(f"Password must be at least {min_length} characters")
                
                if not any(c.isupper() for c in password):
                    errors.append("Password must contain an uppercase letter")
                
                if not any(c.isdigit() for c in password):
                    errors.append("Password must contain a digit")
                
                if not any(c in "!@#$%^&*" for c in password):
                    errors.append("Password must contain a special character (!@#$%^&*)")
                
                if errors:
                    raise ValidationError(
                        "Password does not meet requirements",
                        field='password',
                        details={'requirements': errors}
                    )
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_username(min_length=3, max_length=50) -> Callable:
        """Validates username format."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                username = data.get('username', '').strip()
                
                if len(username) < min_length:
                    raise ValidationError(
                        f"Username must be at least {min_length} characters",
                        field='username'
                    )
                
                if len(username) > max_length:
                    raise ValidationError(
                        f"Username cannot exceed {max_length} characters",
                        field='username'
                    )
                
                if not all(c.isalnum() or c in '_-' for c in username):
                    raise ValidationError(
                        "Username can only contain alphanumeric characters, hyphens, and underscores",
                        field='username'
                    )
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_positive_number(field_name='value') -> Callable:
        """Validates that a field contains a positive number."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                data = request.get_json() or {}
                value = data.get(field_name)
                
                try:
                    num_value = float(value)
                    if num_value <= 0:
                        raise ValueError("Must be positive")
                except (TypeError, ValueError):
                    raise ValidationError(
                        f"{field_name} must be a positive number",
                        field=field_name
                    )
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
