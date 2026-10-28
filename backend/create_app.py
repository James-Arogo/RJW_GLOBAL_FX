from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from config import get_config
from models import db
from routes.auth_routes import auth_routes
from routes.trade_routes import trade_routes
from routes.admin_routes import admin_routes


def create_app(config_name='development'):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        Config = get_config()
        app.config.from_object(Config)
    
    # Enable Cross-Origin Resource Sharing
    CORS(app)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize SocketIO for real-time features
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize the SQLAlchemy database
    db.init_app(app)
    
    # Register application blueprints
    app.register_blueprint(auth_routes, url_prefix="/api/auth")
    app.register_blueprint(trade_routes, url_prefix="/api/trade")
    app.register_blueprint(admin_routes, url_prefix="/api/admin")
    
    # Root route
    @app.route("/")
    def home():
        return jsonify({
            "app_name": "RJW GLOBAL FX Backend",
            "status": "Running in Development Mode",
            "message": "Welcome to the RJW GLOBAL FX API 💹",
            "developers":"RJW~/MAN@BACKEND.KE"
                             "  ENG~OPELLA"
                              " CJO~AROGO"
        }), 200
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app, socketio
