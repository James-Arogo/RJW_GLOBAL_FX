"""
RJW GLOBAL FX - Clean Flask Application
Production-ready, minimal setup
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import get_config

# Initialize extensions (no db yet)
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()

# Create app
app = Flask(__name__, template_folder='templates')

# Load config
Config = get_config()
app.config.from_object(Config)

# Initialize extensions with app
CORS(app)
db.init_app(app)
jwt.init_app(app)
socketio.init_app(app, cors_allowed_origins="*")
mail.init_app(app)

# ============================================
# ROUTES - Define after db initialization
# ============================================

@app.route('/')
def home():
    return jsonify({
        "app_name": "RJW GLOBAL FX Backend",
        "status": "Running in Development Mode",
        "message": "Welcome to the RJW GLOBAL FX API 💹",
        "developers": "RJW~/MAN@BACKEND.KE, ENG~OPELLA, CJO~AROGO"
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    from flask import request
    
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        # Validate
        if not username or len(username) < 3:
            return jsonify({
                "status": "error",
                "message": "Username must be at least 3 characters",
                "code": 400
            }), 400
        
        if not email or '@' not in email:
            return jsonify({
                "status": "error",
                "message": "Valid email required",
                "code": 400
            }), 400
        
        if len(password) < 8:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 8 characters",
                "code": 400
            }), 400

        # Import models after app is initialized
        from models import User
        from werkzeug.security import generate_password_hash

        # Check if exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                "status": "error",
                "message": "Username already exists",
                "code": 400
            }), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                "status": "error",
                "message": "Email already exists",
                "code": 400
            }), 400

        # Create user
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_verified=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Registration successful!",
            "code": 201,
            "data": {
                "username": username,
                "email": email,
                "balance": 1000.00
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    from flask import request
    from flask_jwt_extended import create_access_token, create_refresh_token
    from werkzeug.security import check_password_hash
    from models import User
    from datetime import datetime
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Username and password required",
                "code": 400
            }), 400

        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({
                "status": "error",
                "message": "Invalid username or password",
                "code": 401
            }), 401

        user.last_login = datetime.utcnow()
        db.session.commit()

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "code": 200,
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "balance": float(user.balance)
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@app.route('/api/trade/live_prices', methods=['GET'])
def live_prices():
    """Get live prices"""
    from utils.market_engine import market_engine
    
    prices = market_engine.get_prices()
    return jsonify(prices), 200


@app.route('/simple-test', methods=['GET'])
def simple_test():
    """Simple test endpoint"""
    return "<h1>Simple Test Works!</h1><p>Backend is running.</p>"


# ============================================
# Error handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "code": 500
    }), 500


# ============================================
# Run application
# ============================================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    socketio.run(app, host="0.0.0.0", port=4000, debug=True, allow_unsafe_werkzeug=True)
