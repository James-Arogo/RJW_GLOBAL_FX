from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.analytics_engine import analytics_engine
from models import db, User

analytics_routes = Blueprint('analytics_routes', __name__)


@analytics_routes.route('/user/performance', methods=['GET'])
@jwt_required()
def user_performance():
    """Get user performance metrics."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    days = request.args.get('days', 30, type=int)
    metrics = analytics_engine.get_user_performance_metrics(user.id, days)
    
    return jsonify(metrics)


@analytics_routes.route('/user/risk', methods=['GET'])
@jwt_required()
def user_risk_metrics():
    """Get user risk metrics."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    risk_metrics = analytics_engine.get_risk_metrics(user.id)
    
    return jsonify(risk_metrics)


@analytics_routes.route('/platform/statistics', methods=['GET'])
@jwt_required()
def platform_statistics():
    """Get platform-wide statistics (admin only)."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    # Simple admin check (you might want to implement proper roles)
    if not user or not user.username.startswith('admin'):
        return jsonify({"message": "Unauthorized"}), 403
    
    stats = analytics_engine.get_platform_statistics()
    
    return jsonify(stats)


@analytics_routes.route('/market/sentiment', methods=['GET'])
@jwt_required()
def market_sentiment():
    """Get market sentiment analysis."""
    sentiment = analytics_engine.get_market_sentiment()
    
    return jsonify(sentiment)


@analytics_routes.route('/user/leaderboard', methods=['GET'])
@jwt_required()
def user_leaderboard():
    """Get user leaderboard based on performance."""
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Get all users and calculate their performance
    users = User.query.all()
    leaderboard = []
    
    for user in users:
        metrics = analytics_engine.get_user_performance_metrics(user.id, days)
        if metrics['total_trades'] > 0:  # Only include users with trades
            leaderboard.append({
                'username': user.username,
                'total_profit_loss': metrics['total_profit_loss'],
                'win_rate': metrics['win_rate'],
                'total_trades': metrics['total_trades'],
                'sharpe_ratio': metrics['sharpe_ratio']
            })
    
    # Sort by total profit loss
    leaderboard.sort(key=lambda x: x['total_profit_loss'], reverse=True)
    
    return jsonify(leaderboard[:limit])


@analytics_routes.route('/user/heatmap', methods=['GET'])
@jwt_required()
def user_trading_heatmap():
    """Get trading activity heatmap data."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    from models import Trade
    from datetime import datetime, timedelta
    import calendar
    
    # Get trades for the last 90 days
    start_date = datetime.utcnow() - timedelta(days=90)
    trades = Trade.query.filter(
        Trade.user_id == user.id,
        Trade.timestamp >= start_date
    ).all()
    
    # Create heatmap data (hour of day vs day of week)
    heatmap_data = {}
    for i in range(7):  # Days of week
        for j in range(24):  # Hours of day
            heatmap_data[f"{i}-{j}"] = 0
    
    for trade in trades:
        day_of_week = trade.timestamp.weekday()
        hour_of_day = trade.timestamp.hour
        key = f"{day_of_week}-{hour_of_day}"
        heatmap_data[key] = heatmap_data.get(key, 0) + 1
    
    # Format for frontend
    heatmap = []
    for day in range(7):
        day_name = calendar.day_name[day]
        day_data = []
        for hour in range(24):
            key = f"{day}-{hour}"
            day_data.append({
                'hour': hour,
                'trades': heatmap_data.get(key, 0)
            })
        heatmap.append({
            'day': day_name,
            'data': day_data
        })
    
    return jsonify(heatmap)


@analytics_routes.route('/user/pair-analysis', methods=['GET'])
@jwt_required()
def user_pair_analysis():
    """Get detailed analysis of user performance by currency pair."""
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    from models import Trade
    from sqlalchemy import func
    
    # Get detailed statistics by pair
    pair_stats = db.session.query(
        Trade.pair,
        func.count(Trade.id).label('total_trades'),
        func.sum(Trade.profit_loss).label('total_profit_loss'),
        func.avg(Trade.amount).label('avg_amount'),
        func.sum(func.case([(Trade.result == 'win', 1)], else_=0)).label('wins')
    ).filter(
        Trade.user_id == user.id
    ).group_by(Trade.pair).all()
    
    analysis = []
    for stat in pair_stats:
        win_rate = (stat.wins / stat.total_trades * 100) if stat.total_trades > 0 else 0
        avg_profit_per_trade = stat.total_profit_loss / stat.total_trades if stat.total_trades > 0 else 0
        
        analysis.append({
            'pair': stat.pair,
            'total_trades': stat.total_trades,
            'total_profit_loss': round(stat.total_profit_loss, 2),
            'avg_amount': round(stat.avg_amount, 2),
            'wins': stat.wins,
            'win_rate': round(win_rate, 2),
            'avg_profit_per_trade': round(avg_profit_per_trade, 2)
        })
    
    return jsonify(analysis)
