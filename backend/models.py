from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# This will be initialized in app.py
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=1000.0)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(500), nullable=True)
    reset_token = db.Column(db.String(500), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    trades = db.relationship('Trade', backref='user', lazy=True)

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pair = db.Column(db.String(10))
    amount = db.Column(db.Float)
    result = db.Column(db.String(20))
    profit_loss = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    trade_type = db.Column(db.String(20), default='market')
    stop_loss = db.Column(db.Float, nullable=True)
    take_profit = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='executed')
    entry_price = db.Column(db.Float, nullable=True)
    exit_price = db.Column(db.Float, nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pair = db.Column(db.String(10))
    amount = db.Column(db.Float)
    order_type = db.Column(db.String(20))
    price = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', backref='orders')

class AdminAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
