from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Trade
from utils.market_engine import market_engine
from werkzeug.security import generate_password_hash


# Create blueprint for API documentation
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api/docs')

# Create API instance
api = Api(
    swagger_bp,
    version='1.0',
    title='RJW GLOBAL FX API',
    description='Comprehensive forex trading simulation API documentation',
    doc='/swagger'
)

# Define namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
trade_ns = api.namespace('trade', description='Trading operations')
admin_ns = api.namespace('admin', description='Administrative operations')

# Define data models
user_model = api.model('User', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

trade_model = api.model('Trade', {
    'pair': fields.String(required=True, description='Currency pair (e.g., EUR/USD)'),
    'amount': fields.Float(required=True, description='Trade amount')
})

price_model = api.model('Price', {
    'EUR/USD': fields.Float(description='EUR/USD exchange rate'),
    'GBP/USD': fields.Float(description='GBP/USD exchange rate'),
    'USD/JPY': fields.Float(description='USD/JPY exchange rate'),
    'XAU/USD': fields.Float(description='Gold price in USD')
})

# Authentication endpoints
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    @auth_ns.doc('register_user')
    def post(self):
        """Register a new user"""
        return {'message': 'User registration endpoint'}, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model)
    @auth_ns.doc('login_user')
    def post(self):
        """Authenticate user and return JWT token"""
        return {'message': 'User login endpoint'}, 200

@auth_ns.route('/profile')
class Profile(Resource):
    @jwt_required()
    @auth_ns.doc('get_user_profile')
    def get(self):
        """Get current user profile"""
        return {'message': 'User profile endpoint'}, 200

# Trading endpoints
@trade_ns.route('/live_prices')
class LivePrices(Resource):
    @trade_ns.marshal_with(price_model)
    @trade_ns.doc('get_live_prices')
    def get(self):
        """Get live market prices"""
        return market_engine.get_prices()

@trade_ns.route('/trade')
class ExecuteTrade(Resource):
    @jwt_required()
    @trade_ns.expect(trade_model)
    @trade_ns.doc('execute_trade')
    def post(self):
        """Execute a trade"""
        return {'message': 'Trade execution endpoint'}, 200

@trade_ns.route('/history/<string:username>')
class TradeHistory(Resource):
    @jwt_required()
    @trade_ns.doc('get_trade_history')
    def get(self, username):
        """Get user trade history"""
        return {'message': 'Trade history endpoint'}, 200

@trade_ns.route('/portfolio/<string:username>')
class Portfolio(Resource):
    @jwt_required()
    @trade_ns.doc('get_portfolio')
    def get(self, username):
        """Get user portfolio statistics"""
        return {'message': 'Portfolio endpoint'}, 200

# Admin endpoints
@admin_ns.route('/status')
class AdminStatus(Resource):
    @admin_ns.doc('get_system_status')
    def get(self):
        """Get system status and statistics"""
        return {'message': 'Admin status endpoint'}, 200
