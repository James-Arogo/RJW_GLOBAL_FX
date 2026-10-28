"""
Standardized API Response Handler
Ensures consistent response format across all endpoints
"""
from datetime import datetime
from flask import jsonify
from typing import Any, Dict, Optional, List


class ResponseHandler:
    """Centralized response handler for all API endpoints."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Request successful",
        status_code: int = 200,
        errors: Optional[List] = None
    ) -> tuple:
        """
        Returns a standardized success response.
        
        Args:
            data: The response data payload
            message: Success message
            status_code: HTTP status code
            errors: Optional list of warnings/errors
        """
        response = {
            "status": "success",
            "code": status_code,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "errors": errors or []
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict] = None
    ) -> tuple:
        """
        Returns a standardized error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
        """
        response = {
            "status": "error",
            "code": status_code,
            "message": message,
            "error_code": error_code,
            "data": None,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(
        items: List,
        total: int,
        page: int,
        per_page: int,
        message: str = "Data retrieved successfully"
    ) -> tuple:
        """
        Returns a standardized paginated response.
        
        Args:
            items: List of items to return
            total: Total number of items
            page: Current page number
            per_page: Items per page
            message: Success message
        """
        response = {
            "status": "success",
            "code": 200,
            "message": message,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(response), 200
    
    @staticmethod
    def created(
        data: Any,
        message: str = "Resource created successfully"
    ) -> tuple:
        """Returns a standardized 201 Created response."""
        return ResponseHandler.success(data, message, 201)
    
    @staticmethod
    def bad_request(message: str, details: Optional[Dict] = None) -> tuple:
        """Returns a 400 Bad Request response."""
        return ResponseHandler.error(message, 400, "BAD_REQUEST", details)
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> tuple:
        """Returns a 401 Unauthorized response."""
        return ResponseHandler.error(message, 401, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message: str = "Forbidden") -> tuple:
        """Returns a 403 Forbidden response."""
        return ResponseHandler.error(message, 403, "FORBIDDEN")
    
    @staticmethod
    def not_found(resource: str = "Resource") -> tuple:
        """Returns a 404 Not Found response."""
        return ResponseHandler.error(
            f"{resource} not found",
            404,
            "NOT_FOUND"
        )
    
    @staticmethod
    def conflict(message: str, details: Optional[Dict] = None) -> tuple:
        """Returns a 409 Conflict response."""
        return ResponseHandler.error(message, 409, "CONFLICT", details)
    
    @staticmethod
    def unprocessable_entity(message: str, details: Optional[Dict] = None) -> tuple:
        """Returns a 422 Unprocessable Entity response."""
        return ResponseHandler.error(message, 422, "VALIDATION_ERROR", details)
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> tuple:
        """Returns a 500 Internal Server Error response."""
        return ResponseHandler.error(message, 500, "INTERNAL_ERROR")
