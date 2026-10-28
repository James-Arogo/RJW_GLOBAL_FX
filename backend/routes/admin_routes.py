from flask import Blueprint, jsonify
from models import User, Trade
from utils.profit_manager import profit_manager

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/admin/status', methods=['GET'])
def admin_status():
    total_users = User.query.count()
    total_trades = Trade.query.count()
    platform_profit = profit_manager.calculate_platform_profit()
    return jsonify({
        "total_users": total_users,
        "total_trades": total_trades,
        "platform_profit": platform_profit,
        "profit_margin": f"{profit_manager.min_profit_margin * 100:.0f}%"
    })
