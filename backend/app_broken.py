from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_mail import Mail
from config import get_config
from extensions import db, socketio, jwt, mail
from utils.error_handler import register_error_handlers


# ==========================================================
# Initialize Flask application
# ==========================================================
app = Flask(__name__, template_folder='templates')

# Load configuration dynamically
Config = get_config()
app.config.from_object(Config)

# Enable Cross-Origin Resource Sharing
CORS(app)

# Initialize JWT
jwt.init_app(app)

# Initialize SocketIO for real-time features
socketio.init_app(app, cors_allowed_origins="*")

# Initialize Flask-Mail
mail.init_app(app)

# Initialize the SQLAlchemy database FIRST
db.init_app(app)

# Register error handlers for standardized responses
register_error_handlers(app)

# NOW import routes after db is initialized
from routes.auth_routes import auth_routes
from routes.trade_routes import trade_routes
from routes.admin_routes import admin_routes
from routes.socketio_routes import socketio as socketio_routes
from routes.order_routes import order_routes
from routes.analytics_routes import analytics_routes

# ==========================================================
# Register application blueprints
# ==========================================================
app.register_blueprint(auth_routes, url_prefix="/api/auth")
app.register_blueprint(trade_routes, url_prefix="/api/trade")
app.register_blueprint(admin_routes, url_prefix="/api/admin")
app.register_blueprint(order_routes, url_prefix="/api/orders")
app.register_blueprint(analytics_routes, url_prefix="/api/analytics")
# app.register_blueprint(swagger_bp)  # Temporarily disabled for troubleshooting


# ==========================================================
# Root (Health Check / Home) Route
# ==========================================================
@app.route("/test-template")
def test_template():
    """Test template rendering."""
    return render_template('verify_email.html')


@app.route("/simple-test")
def simple_test():
    """Simple test without template."""
    return "<h1>Simple Test Works!</h1><p>If you see this, the app is running.</p>"


@app.route("/")
def home():
    return render_template('dashboard.html'), 200

@app.route("/api")
def api_home():
    return jsonify({
        "app_name": "RJW GLOBAL FX Backend",
        "status": "Running in Development Mode",
        "message": "Welcome to the RJW GLOBAL FX API 💹",
        "dashboard": "http://localhost:4000/",
        "developers":"RJW~/MAN@BACKEND.KE, ENG~OPELLA, CJO~AROGO"
    }), 200


@app.route("/verify-email")
def verify_email_page():
    """Email verification page."""
    return render_template('verify_email.html')


@app.route("/reset-password")
def reset_password_page():
    """Password reset page."""
    return render_template('reset_password.html')


@app.route("/docs")
def api_docs():
    """API Documentation page."""
    return render_template('api_docs.html')


# ==========================================================
# Create all tables before first request
# ==========================================================
with app.app_context():
    db.create_all()

# Start background services
from routes.socketio_routes import start_price_broadcast
start_price_broadcast()


# ==========================================================
# Run Application Entry Point
# ==========================================================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=4000, debug=True, allow_unsafe_werkzeug=True)
