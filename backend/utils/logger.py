import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from functools import wraps
from flask import request, g
from flask_jwt_extended import get_jwt_identity
import json


class ForexLogger:
    """Comprehensive logging system for the forex trading platform."""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging with Flask app."""
        self.app = app
        
        # Create logs directory if it doesn't exist
        log_dir = app.config.get('LOG_DIR', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure main logger
        self.logger = logging.getLogger('forex_platform')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        json_formatter = logging.Formatter('%(message)s')
        
        # File handlers with rotation
        # General log file
        general_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_handler.setFormatter(detailed_formatter)
        general_handler.setLevel(logging.INFO)
        
        # Error log file
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'errors.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Security log file (JSON format)
        security_handler = RotatingFileHandler(
            os.path.join(log_dir, 'security.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        security_handler.setFormatter(json_formatter)
        security_handler.setLevel(logging.INFO)
        
        # Trading log file (JSON format)
        trading_handler = RotatingFileHandler(
            os.path.join(log_dir, 'trading.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        trading_handler.setFormatter(json_formatter)
        trading_handler.setLevel(logging.INFO)
        
        # Performance log file
        performance_handler = RotatingFileHandler(
            os.path.join(log_dir, 'performance.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        performance_handler.setFormatter(detailed_formatter)
        performance_handler.setLevel(logging.INFO)
        
        # Add handlers to logger
        self.logger.addHandler(general_handler)
        self.logger.addHandler(error_handler)
        
        # Create specialized loggers
        self.security_logger = logging.getLogger('forex_security')
        self.security_logger.addHandler(security_handler)
        self.security_logger.setLevel(logging.INFO)
        
        self.trading_logger = logging.getLogger('forex_trading')
        self.trading_logger.addHandler(trading_handler)
        self.trading_logger.setLevel(logging.INFO)
        
        self.performance_logger = logging.getLogger('forex_performance')
        self.performance_logger.addHandler(performance_handler)
        self.performance_logger.setLevel(logging.INFO)
        
        # Console handler for development
        if app.config.get('DEBUG', False):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(console_handler)
    
    def log_security_event(self, event_type, details, user=None, ip_address=None):
        """Log security-related events."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'user': user or get_jwt_identity() or 'anonymous',
            'ip_address': ip_address or request.environ.get('REMOTE_ADDR', 'unknown'),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        self.security_logger.info(json.dumps(log_entry))
    
    def log_trading_event(self, event_type, details, user=None):
        """Log trading-related events."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'user': user or get_jwt_identity() or 'unknown'
        }
        
        self.trading_logger.info(json.dumps(log_entry))
    
    def log_performance_metric(self, metric_name, value, details=None):
        """Log performance metrics."""
        message = f"METRIC: {metric_name} = {value}"
        if details:
            message += f" | Details: {details}"
        
        self.performance_logger.info(message)
    
    def log_error(self, error, context=None):
        """Log application errors."""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.logger.error(f"Application Error: {json.dumps(error_info)}")
    
    def log_info(self, message, context=None):
        """Log general information."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        
        self.logger.info(message)
    
    def log_warning(self, message, context=None):
        """Log warnings."""
        if context:
            message = f"{message} | Context: {json.dumps(context)}"
        
        self.logger.warning(message)


# Global logger instance
forex_logger = ForexLogger()


def log_security_event(event_type, details, user=None, ip_address=None):
    """Decorator to log security events."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                forex_logger.log_security_event(
                    event_type,
                    details,
                    user=user or get_jwt_identity(),
                    ip_address=request.environ.get('REMOTE_ADDR')
                )
                return result
            except Exception as e:
                forex_logger.log_security_event(
                    f"{event_type}_FAILED",
                    f"{details} | Error: {str(e)}",
                    user=user or get_jwt_identity(),
                    ip_address=request.environ.get('REMOTE_ADDR')
                )
                raise
        return decorated_function
    return decorator


def log_trading_event(event_type, details):
    """Decorator to log trading events."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                forex_logger.log_trading_event(
                    event_type,
                    details,
                    user=get_jwt_identity()
                )
                return result
            except Exception as e:
                forex_logger.log_trading_event(
                    f"{event_type}_FAILED",
                    f"{details} | Error: {str(e)}",
                    user=get_jwt_identity()
                )
                raise
        return decorated_function
    return decorator


def monitor_performance(metric_name):
    """Decorator to monitor function performance."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = f(*args, **kwargs)
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                forex_logger.log_performance_metric(
                    f"{metric_name}_duration",
                    f"{duration:.4f}s",
                    f"function: {f.__name__}"
                )
                
                return result
            except Exception as e:
                end_time = datetime.utcnow()
                duration = (end_time - start_time).total_seconds()
                
                forex_logger.log_performance_metric(
                    f"{metric_name}_error_duration",
                    f"{duration:.4f}s",
                    f"function: {f.__name__} | error: {str(e)}"
                )
                raise
        return decorated_function
    return decorator


class RequestLogger:
    """Middleware to log all HTTP requests."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize request logging middleware."""
        @app.before_request
        def before_request():
            g.start_time = datetime.utcnow()
            
            # Log request details for sensitive endpoints
            if request.endpoint and any(x in request.endpoint for x in ['auth', 'trade', 'admin']):
                forex_logger.log_security_event(
                    'API_REQUEST',
                    {
                        'method': request.method,
                        'endpoint': request.endpoint,
                        'path': request.path,
                        'args': dict(request.args),
                        'json': dict(request.get_json(silent=True) or {})
                    },
                    ip_address=request.environ.get('REMOTE_ADDR')
                )
        
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                end_time = datetime.utcnow()
                duration = (end_time - g.start_time).total_seconds()
                
                forex_logger.log_performance_metric(
                    'request_duration',
                    f"{duration:.4f}s",
                    f"method: {request.method} | path: {request.path} | status: {response.status_code}"
                )
            
            return response
        
        @app.teardown_appcontext
        def teardown_request(exception):
            if exception:
                forex_logger.log_error(
                    exception,
                    {
                        'method': request.method,
                        'path': request.path,
                        'endpoint': request.endpoint
                    }
                )


# Global request logger instance
request_logger = RequestLogger()
