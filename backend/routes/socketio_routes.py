from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import socketio
from utils.market_engine import market_engine
from models import db, User, Trade
import threading
import time


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to RJW GLOBAL FX real-time updates'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('join_room')
@jwt_required()
def handle_join_room(data):
    """Handle joining a user-specific room."""
    username = get_jwt_identity()
    room = f"user_{username}"
    join_room(room)
    emit('status', {'message': f'Joined room for {username}'})


@socketio.on('leave_room')
@jwt_required()
def handle_leave_room(data):
    """Handle leaving a user-specific room."""
    username = get_jwt_identity()
    room = f"user_{username}"
    leave_room(room)
    emit('status', {'message': f'Left room for {username}'})


@socketio.on('subscribe_prices')
def handle_subscribe_prices():
    """Handle subscription to live price updates."""
    emit('status', {'message': 'Subscribed to live price updates'})


def broadcast_price_updates():
    """Background task to broadcast price updates."""
    from extensions import socketio
    while True:
        try:
            prices = market_engine.get_prices()
            socketio.emit('price_update', prices)
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Error broadcasting prices: {e}")
            time.sleep(5)


def start_price_broadcast():
    """Start the price broadcast background thread."""
    price_thread = threading.Thread(target=broadcast_price_updates, daemon=True)
    price_thread.start()


# Don't start the background thread on import
# It will be started after app initialization
