"""Shared Flask extensions to avoid circular imports."""

from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
socketio = SocketIO()
jwt = JWTManager()
mail = Mail()
db = SQLAlchemy()
