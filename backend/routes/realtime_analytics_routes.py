"""
Real-time Analytics API Routes
Provides WebSocket and REST endpoints for live trading analytics
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room, disconnect
from models import User, Trade
from utils.realtime_trade_analytics import realtime_trade_analytics
import json

realtime_analytics_routes = Blueprint('realtime_analytics_routes', __name__)

# ========== REST ENDPOINTS ==========

@realtime_analytics_routes.route('/live/user-metrics', methods=['GET'])
@jwt_required()
def get_user_metrics():
    """Get live user trading metrics"""
    current_user = get_jwt_identity()
    metrics = realtime_trade_analytics.get_live_user_metrics(current_user)
    
    if not metrics:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(metrics), 200


@realtime_analytics_routes.route('/live/pair-metrics/<pair>', methods=['GET'])
@jwt_required()
def get_pair_metrics(pair):
    """Get live metrics for a specific pair"""
    current_user = get_jwt_identity()
    metrics = realtime_trade_analytics.get_live_pair_metrics(current_user, pair)
    
    if not metrics:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(metrics), 200


@realtime_analytics_routes.route('/live/platform-metrics', methods=['GET'])
@jwt_required()
def get_platform_metrics():
    """Get live platform metrics"""
    metrics = realtime_trade_analytics.get_live_platform_metrics()
    return jsonify(metrics), 200


@realtime_analytics_routes.route('/live/trade-stream', methods=['GET'])
@jwt_required()
def get_trade_stream():
    """Get live trade stream"""
    current_user = get_jwt_identity()
    limit = request.args.get('limit', 50, type=int)
    trades = realtime_trade_analytics.get_live_trade_stream(current_user, limit)
    
    return jsonify({
        'trades': trades,
        'total': len(trades)
    }), 200


@realtime_analytics_routes.route('/live/risk-metrics', methods=['GET'])
@jwt_required()
def get_risk_metrics():
    """Get real-time risk metrics"""
    current_user = get_jwt_identity()
    metrics = realtime_trade_analytics.get_live_risk_metrics(current_user)
    
    if not metrics:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(metrics), 200


@realtime_analytics_routes.route('/live/pair-comparison', methods=['GET'])
@jwt_required()
def get_pair_comparison():
    """Get pair performance comparison"""
    current_user = get_jwt_identity()
    comparison = realtime_trade_analytics.get_pair_comparison(current_user)
    
    return jsonify({
        'pairs': comparison,
        'total_pairs': len(comparison)
    }), 200


@realtime_analytics_routes.route('/live/performance-trend', methods=['GET'])
@jwt_required()
def get_performance_trend():
    """Get performance trend data"""
    current_user = get_jwt_identity()
    timeframe = request.args.get('timeframe', 60, type=int)
    trend = realtime_trade_analytics.get_performance_trend(current_user, timeframe)
    
    return jsonify({
        'trend': trend,
        'timeframe_minutes': timeframe,
        'data_points': len(trend)
    }), 200


@realtime_analytics_routes.route('/live/hourly-performance', methods=['GET'])
@jwt_required()
def get_hourly_performance():
    """Get hourly performance breakdown"""
    current_user = get_jwt_identity()
    days = request.args.get('days', 7, type=int)
    hourly = realtime_trade_analytics.get_hourly_performance(current_user, days)
    
    return jsonify({
        'hourly_data': hourly,
        'days': days,
        'total_hours': len(hourly)
    }), 200


@realtime_analytics_routes.route('/live/dashboard', methods=['GET'])
@jwt_required()
def get_complete_dashboard():
    """Get complete realtime dashboard"""
    current_user = get_jwt_identity()
    dashboard = realtime_trade_analytics.get_complete_realtime_dashboard(current_user)
    
    if not dashboard:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(dashboard), 200
