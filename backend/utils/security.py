import time
import hashlib
from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from utils.logger import forex_logger


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key, limit, window):
        """Check if request is allowed based on rate limit."""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < window]
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit=100, window=60, key_func=None):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate key for rate limiting
            if key_func:
                key = key_func()
            else:
                key = request.environ.get('REMOTE_ADDR', 'unknown')
            
            # Add endpoint to key for more specific limiting
            key = f"{key}:{request.endpoint}"
            
            if not rate_limiter.is_allowed(key, limit, window):
                forex_logger.log_security_event(
                    'RATE_LIMIT_EXCEEDED',
                    f'Rate limit exceeded for {request.endpoint}',
                    ip_address=request.environ.get('REMOTE_ADDR')
                )
                return jsonify({
                    "message": "Rate limit exceeded. Please try again later.",
                    "retry_after": window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_verified_email():
    """Decorator to require email verification."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            if not current_user:
                return jsonify({"message": "Authentication required"}), 401
            
            from models import User
            user = User.query.filter_by(username=current_user).first()
            if not user:
                return jsonify({"message": "User not found"}), 404
            
            if not user.is_verified:
                return jsonify({"message": "Email verification required"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_input(schema):
    """Input validation decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"message": "JSON data required"}), 400
                
                # Basic validation based on schema
                for field, field_type in schema.items():
                    if field in data and data[field] is not None:
                        if not isinstance(data[field], field_type):
                            return jsonify({
                                "message": f"Field '{field}' must be of type {field_type.__name__}"
                            }), 400
                
                return f(*args, **kwargs)
            except Exception as e:
                forex_logger.log_error(e, {"endpoint": request.endpoint})
                return jsonify({"message": "Invalid input data"}), 400
        return decorated_function
    return decorator


def sanitize_input(text):
    """Sanitize text input to prevent XSS."""
    if not text:
        return text
    
    # Basic XSS prevention
    dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'vbscript:', 'onload=', 'onerror=']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized


def get_client_ip():
    """Get client IP address considering proxies."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.environ.get('REMOTE_ADDR')


def log_security_event(event_type, details, user=None):
    """Log security events."""
    forex_logger.log_security_event(
        event_type,
        details,
        user=user or get_jwt_identity(),
        ip_address=get_client_ip()
    )


def generate_csrf_token():
    """Generate CSRF token."""
    token = hashlib.sha256(f"{time.time()}{get_client_ip()}".encode()).hexdigest()
    return token


def validate_csrf_token(token):
    """Validate CSRF token (simplified)."""
    # In production, use a more robust CSRF protection
    return token and len(token) == 64


class SecurityHeaders:
    """Security headers middleware."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security headers middleware."""
        @app.after_request
        def add_security_headers(response):
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Enable XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Force HTTPS in production
            if app.config.get('FORCE_HTTPS', False):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response.headers['Content-Security-Policy'] = csp
            
            # Referrer policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions policy
            permissions_policy = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            )
            response.headers['Permissions-Policy'] = permissions_policy
            
            return response


# Global security headers instance
security_headers = SecurityHeaders()


def check_password_strength(password):
    """Check password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def detect_suspicious_activity(user):
    """Detect suspicious user activity."""
    from models import User, AdminAudit
    from datetime import datetime, timedelta
    
    # Check for multiple failed login attempts
    recent_failures = AdminAudit.query.filter(
        AdminAudit.action.like('%login%'),
        AdminAudit.timestamp >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    if recent_failures > 10:
        return True, "Multiple failed login attempts detected"
    
    # Check for rapid API calls
    recent_api_calls = AdminAudit.query.filter(
        AdminAudit.action.like('%API_REQUEST%'),
        AdminAudit.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).count()
    
    if recent_api_calls > 100:
        return True, "Unusual API activity detected"
    
    return False, "No suspicious activity detected"
