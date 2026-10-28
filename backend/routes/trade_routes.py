from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.market_engine import market_engine
from utils.profit_manager import profit_manager
from models import db, User, Trade
from extensions import socketio

trade_routes = Blueprint('trade_routes', __name__)

@trade_routes.route('/live_prices', methods=['GET'])
def live_prices():
    return jsonify(market_engine.get_prices())

@trade_routes.route('/trade', methods=['POST'])
@jwt_required()
def execute_trade():
    current_user = get_jwt_identity()
    data = request.get_json()
    pair = data.get('pair')
    amount = float(data.get('amount'))

    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if user.balance < amount:
        return jsonify({"message": "Insufficient balance"}), 400
    
    if pair not in market_engine.prices:
        return jsonify({"message": "Invalid currency pair"}), 400

    result = market_engine.execute_trade(pair, amount)
    result = profit_manager.enforce_margin(result)

    trade = Trade(
        user_id=user.id,
        pair=pair,
        amount=amount,
        result=result["result"],
        profit_loss=result["profit_loss"]
    )

    user.balance += result["profit_loss"]
    db.session.add(trade)
    db.session.commit()

    # Emit real-time trade update to user's room
    socketio.emit('trade_update', {
        'pair': pair,
        'result': result["result"],
        'profit_loss': result["profit_loss"],
        'balance': round(user.balance, 2)
    }, room=f"user_{current_user}")

    return jsonify({
        "pair": pair,
        "result": result["result"],
        "profit_loss": result["profit_loss"],
        "balance": round(user.balance, 2)
    })


@trade_routes.route('/history/<username>', methods=['GET'])
@jwt_required()
def get_trade_history(username):
    current_user = get_jwt_identity()
    
    # Users can only see their own trade history
    if current_user != username:
        return jsonify({"message": "Unauthorized"}), 403
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    trades = Trade.query.filter_by(user_id=user.id).order_by(Trade.timestamp.desc()).limit(50).all()
    
    return jsonify([{
        'id': trade.id,
        'pair': trade.pair,
        'amount': trade.amount,
        'result': trade.result,
        'profit_loss': trade.profit_loss,
        'timestamp': trade.timestamp.isoformat()
    } for trade in trades])


@trade_routes.route('/portfolio/<username>', methods=['GET'])
@jwt_required()
def get_portfolio(username):
    current_user = get_jwt_identity()
    
    # Users can only see their own portfolio
    if current_user != username:
        return jsonify({"message": "Unauthorized"}), 403
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    trades = Trade.query.filter_by(user_id=user.id).all()
    
    # Calculate portfolio statistics
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.result == 'win'])
    losing_trades = len([t for t in trades if t.result == 'loss'])
    total_profit_loss = sum(t.profit_loss for t in trades)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Group trades by currency pair
    pair_stats = {}
    for trade in trades:
        if trade.pair not in pair_stats:
            pair_stats[trade.pair] = {
                'trades': 0,
                'profit_loss': 0,
                'wins': 0
            }
        pair_stats[trade.pair]['trades'] += 1
        pair_stats[trade.pair]['profit_loss'] += trade.profit_loss
        if trade.result == 'win':
            pair_stats[trade.pair]['wins'] += 1
    
    return jsonify({
        'balance': user.balance,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
        'total_profit_loss': round(total_profit_loss, 2),
        'pair_statistics': pair_stats
    })
