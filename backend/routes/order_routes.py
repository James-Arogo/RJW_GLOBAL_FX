from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.order_manager import order_manager
from models import db, User, Order
from extensions import socketio

order_routes = Blueprint('order_routes', __name__)


@order_routes.route('/limit', methods=['POST'])
@jwt_required()
def create_limit_order():
    """Create a limit order."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    pair = data.get('pair')
    amount = float(data.get('amount'))
    target_price = float(data.get('target_price'))
    
    if user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    
    order = order_manager.create_limit_order(user.id, pair, amount, target_price)
    
    return jsonify({
        "message": "Limit order created successfully",
        "order_id": order.id,
        "pair": order.pair,
        "amount": order.amount,
        "target_price": order.price,
        "status": order.status
    }), 201


@order_routes.route('/stop_loss', methods=['POST'])
@jwt_required()
def create_stop_loss_order():
    """Create a stop-loss order."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    pair = data.get('pair')
    amount = float(data.get('amount'))
    stop_price = float(data.get('stop_price'))
    
    if user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    
    order = order_manager.create_stop_loss_order(user.id, pair, amount, stop_price)
    
    return jsonify({
        "message": "Stop-loss order created successfully",
        "order_id": order.id,
        "pair": order.pair,
        "amount": order.amount,
        "stop_price": order.price,
        "status": order.status
    }), 201


@order_routes.route('/take_profit', methods=['POST'])
@jwt_required()
def create_take_profit_order():
    """Create a take-profit order."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    pair = data.get('pair')
    amount = float(data.get('amount'))
    target_price = float(data.get('target_price'))
    
    if user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    
    order = order_manager.create_take_profit_order(user.id, pair, amount, target_price)
    
    return jsonify({
        "message": "Take-profit order created successfully",
        "order_id": order.id,
        "pair": order.pair,
        "amount": order.amount,
        "target_price": order.price,
        "status": order.status
    }), 201


@order_routes.route('/cancel/<int:order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    """Cancel a pending order."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    success = order_manager.cancel_order(order_id, user.id)
    
    if success:
        return jsonify({"message": "Order cancelled successfully"})
    else:
        return jsonify({"message": "Order not found or cannot be cancelled"}), 404


@order_routes.route('/list', methods=['GET'])
@jwt_required()
def list_orders():
    """Get user's orders."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    status = request.args.get('status')  # Optional filter by status
    orders = order_manager.get_user_orders(user.id, status)
    
    return jsonify([{
        'id': order.id,
        'pair': order.pair,
        'amount': order.amount,
        'order_type': order.order_type,
        'price': order.price,
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'executed_at': order.executed_at.isoformat() if order.executed_at else None
    } for order in orders])


@order_routes.route('/statistics', methods=['GET'])
@jwt_required()
def order_statistics():
    """Get order execution statistics."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    stats = order_manager.get_order_statistics(user.id)
    return jsonify(stats)


@order_routes.route('/check_pending', methods=['POST'])
@jwt_required()
def check_pending_orders():
    """Manually trigger order execution check (for testing)."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    executed_orders = order_manager.check_pending_orders()
    
    # Emit real-time updates for executed orders
    for executed_order in executed_orders:
        socketio.emit('order_executed', {
            'order_id': executed_order['order_id'],
            'pair': executed_order['pair'],
            'amount': executed_order['amount'],
            'execution_price': executed_order['execution_price'],
            'profit_loss': executed_order['profit_loss']
        }, room=f"user_{current_user}")
    
    return jsonify({
        "message": f"Checked pending orders. Executed {len(executed_orders)} orders.",
        "executed_orders": executed_orders
    })
