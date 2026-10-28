"""
Custom Exception Classes and Error Handling
Provides application-specific exceptions with proper categorization
"""
from functools import wraps
from flask import jsonify, request
from utils.api_response import ResponseHandler
import traceback


# ========== Custom Exception Classes ==========

class ForexException(Exception):
    """Base exception for all Forex trading exceptions."""
    def __init__(self, message, error_code="GENERIC_ERROR", status_code=400, details=None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ForexException):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed", details=None):
        super().__init__(message, "AUTH_ERROR", 401, details)


class InvalidCredentialsError(AuthenticationError):
    """Raised when username or password is invalid."""
    def __init__(self):
        super().__init__(
            "Invalid username or password",
            error_code="INVALID_CREDENTIALS"
        )


class UnauthorizedError(ForexException):
    """Raised when user is not authorized for an action."""
    def __init__(self, message="Unauthorized", details=None):
        super().__init__(message, "UNAUTHORIZED", 403, details)


class ValidationError(ForexException):
    """Raised when input validation fails."""
    def __init__(self, message, field=None, details=None):
        if field:
            message = f"Validation error in '{field}': {message}"
        details = details or {}
        if field:
            details['field'] = field
        super().__init__(message, "VALIDATION_ERROR", 422, details)


class ResourceNotFoundError(ForexException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type="Resource", details=None):
        message = f"{resource_type} not found"
        super().__init__(message, "NOT_FOUND", 404, details)


class InsufficientBalanceError(ForexException):
    """Raised when user doesn't have enough balance."""
    def __init__(self, balance, required, details=None):
        details = details or {}
        details['balance'] = balance
        details['required'] = required
        message = f"Insufficient balance. Available: {balance}, Required: {required}"
        super().__init__(message, "INSUFFICIENT_BALANCE", 400, details)


class InvalidPairError(ValidationError):
    """Raised when an invalid currency pair is used."""
    def __init__(self, pair, available_pairs=None):
        details = {'pair': pair, 'available_pairs': available_pairs}
        super().__init__(
            f"Invalid currency pair: {pair}",
            field='pair',
            details=details
        )


class OrderExecutionError(ForexException):
    """Raised when order execution fails."""
    def __init__(self, message, order_id=None, details=None):
        details = details or {}
        if order_id:
            details['order_id'] = order_id
        super().__init__(message, "ORDER_EXECUTION_ERROR", 400, details)


class DuplicateResourceError(ForexException):
    """Raised when trying to create a duplicate resource."""
    def __init__(self, resource_type, value, field=None):
        details = {
            'field': field or 'unknown',
            'value': value
        }
        message = f"{resource_type} with this {field or 'field'} already exists"
        super().__init__(message, "DUPLICATE_RESOURCE", 409, details)


class RateLimitExceededError(ForexException):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after=None):
        details = {}
        if retry_after:
            details['retry_after'] = retry_after
        super().__init__(
            "Too many requests. Please try again later.",
            "RATE_LIMIT_EXCEEDED",
            429,
            details
        )


# ========== Error Handler Decorator ==========

def handle_exceptions(f):
    """
    Decorator to handle exceptions in route handlers.
    Catches all exceptions and returns standardized error responses.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ForexException as e:
            return ResponseHandler.error(
                e.message,
                e.status_code,
                e.error_code,
                e.details
            )
        except ValueError as e:
            return ResponseHandler.bad_request(
                f"Invalid value: {str(e)}",
                {'error': str(e)}
            )
        except TypeError as e:
            return ResponseHandler.bad_request(
                "Invalid request format",
                {'error': str(e)}
            )
        except Exception as e:
            # Log the full traceback for debugging
            print(f"Unhandled exception in {f.__name__}: {str(e)}")
            traceback.print_exc()
            return ResponseHandler.internal_error(
                "An unexpected error occurred. Please try again later."
            )
    return decorated_function


def error_response(status_code=400, error_code="ERROR"):
    """
    Decorator factory for creating custom error handlers.
    Usage: @error_response(400, "CUSTOM_ERROR")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                return ResponseHandler.error(
                    str(e),
                    status_code,
                    error_code
                )
        return decorated_function
    return decorator


# ========== Global Error Handler for Flask ==========

def register_error_handlers(app):
    """Register global error handlers for the Flask app."""
    
    @app.errorhandler(ForexException)
    def handle_forex_exception(error):
        return ResponseHandler.error(
            error.message,
            error.status_code,
            error.error_code,
            error.details
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return ResponseHandler.not_found("Endpoint")
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return ResponseHandler.error(
            "Method not allowed",
            405,
            "METHOD_NOT_ALLOWED"
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return ResponseHandler.internal_error()
