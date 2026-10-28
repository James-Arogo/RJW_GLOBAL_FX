from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, AdminAudit
from datetime import datetime, timedelta

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        # Validate input
        if not username or len(username) < 3:
            return jsonify({
                "status": "error",
                "message": "Username must be at least 3 characters long",
                "code": 400
            }), 400
        
        if not email or '@' not in email:
            return jsonify({
                "status": "error",
                "message": "Valid email address required",
                "code": 400
            }), 400
        
        if len(password) < 8:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 8 characters",
                "code": 400
            }), 400

        # Check if user exists
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
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_verified=True  # Auto-verify for demo
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Registration successful! Please login.",
            "code": 201,
            "data": {
                "username": username,
                "email": email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@auth_routes.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens"""
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

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create tokens
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


@auth_routes.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user profile"""
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found",
                "code": 404
            }), 404

        return jsonify({
            "status": "success",
            "code": 200,
            "data": {
                "username": user.username,
                "email": user.email,
                "balance": float(user.balance),
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@auth_routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT token"""
    try:
        username = get_jwt_identity()
        access_token = create_access_token(identity=username)

        return jsonify({
            "status": "success",
            "code": 200,
            "data": {
                "access_token": access_token
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    return jsonify({
        "status": "success",
        "message": "Logged out successfully",
        "code": 200
    }), 200
