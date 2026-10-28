from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, AdminAudit
from datetime import datetime, timedelta
from utils.email_service import email_service
from utils.logger import forex_logger, log_security_event, log_trading_event
from utils.security import rate_limit, validate_input, check_password_strength, sanitize_input

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
@rate_limit(limit=5, window=300)  # 5 registrations per 5 minutes
@log_security_event('USER_REGISTRATION', 'New user registration attempt')
@validate_input({'username': str, 'email': str, 'password': str})
def register():
    data = request.get_json()
    username = sanitize_input(data.get('username', '').strip())
    email = sanitize_input(data.get('email', '').strip().lower())
    password = data.get('password')

    # Validate input
    if not username or len(username) < 3:
        return jsonify({"message": "Username must be at least 3 characters long"}), 400
    
    if not email or '@' not in email:
        return jsonify({"message": "Valid email address required"}), 400
    
    # Check password strength
    is_strong, message = check_password_strength(password)
    if not is_strong:
        return jsonify({"message": message}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed = generate_password_hash(password)
    verification_token = email_service.generate_verification_token(None)
    
    user = User(
        username=username, 
        email=email, 
        password=hashed,
        verification_token=verification_token
    )
    db.session.add(user)
    db.session.commit()
    
    # Send verification email
    if email_service.send_verification_email(email, verification_token):
        message = "Registration successful. Please check your email to verify your account."
    else:
        message = "Registration successful, but verification email failed to send."
    
    # Log admin audit
    audit = AdminAudit(action=f"User registration: {username}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"message": message}), 201

@auth_routes.route('/login', methods=['POST'])
@rate_limit(limit=10, window=300)  # 10 login attempts per 5 minutes
@log_security_event('USER_LOGIN', 'User login attempt')
@validate_input({'username': str, 'password': str})
def login():
    data = request.get_json()
    username = sanitize_input(data.get('username', '').strip())
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        
        # Log admin audit
        audit = AdminAudit(action=f"User login: {username}")
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            "message": "Login successful", 
            "username": username, 
            "email": user.email,
            "is_verified": user.is_verified,
            "balance": user.balance,
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    # Log failed login attempt
    log_security_event('LOGIN_FAILED', f'Failed login attempt for username: {username}')
    return jsonify({"message": "Invalid credentials"}), 401


@auth_routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_token})


@auth_routes.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "username": user.username,
        "balance": user.balance,
        "created_at": user.created_at.isoformat()
    })


@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    
    # Log admin audit
    audit = AdminAudit(action=f"User logout: {current_user}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"message": "Logout successful"})


@auth_routes.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify email address with token."""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"message": "Verification token required"}), 400
    
    user_id = email_service.verify_token(token, 'email_verification')
    if not user_id:
        return jsonify({"message": "Invalid or expired verification token"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    # Send welcome email
    email_service.send_welcome_email(user.email, user.username)
    
    # Log admin audit
    audit = AdminAudit(action=f"Email verified: {user.username}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"message": "Email verified successfully"}), 200


@auth_routes.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200
    
    # Generate new verification token
    verification_token = email_service.generate_verification_token(user.id)
    user.verification_token = verification_token
    db.session.commit()
    
    # Send verification email
    if email_service.send_verification_email(email, verification_token):
        return jsonify({"message": "Verification email sent successfully"}), 200
    else:
        return jsonify({"message": "Failed to send verification email"}), 500


@auth_routes.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "If email exists, password reset instructions have been sent"}), 200
    
    # Generate reset token
    reset_token = email_service.generate_password_reset_token(user.id)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    
    # Send reset email
    if email_service.send_password_reset_email(email, reset_token):
        return jsonify({"message": "Password reset instructions sent to your email"}), 200
    else:
        return jsonify({"message": "Failed to send reset email"}), 500


@auth_routes.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({"message": "Token and new password required"}), 400
    
    user_id = email_service.verify_token(token, 'password_reset')
    if not user_id:
        return jsonify({"message": "Invalid or expired reset token"}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Update password
    user.password = generate_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()
    
    # Log admin audit
    audit = AdminAudit(action=f"Password reset: {user.username}")
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({"message": "Password reset successfully"}), 200
