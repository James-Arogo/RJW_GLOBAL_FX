"""
Real-time Trade Analytics Engine
Provides live trade metrics and statistics
"""

from datetime import datetime, timedelta
from models import db, Trade, User
from utils.currency_converter import currency_converter


class RealtimeAnalytics:
    """Real-time analytics for trades"""
    
    @staticmethod
    def get_user_realtime_stats(username):
        """Get real-time stats for a user"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        # Get all trades for user
        trades = Trade.query.filter_by(user_id=user.id).all()
        
        if not trades:
            return {
                'username': username,
                'total_trades': 0,
                'balance_usd': user.balance,
                'balance_ksh': currency_converter.usd_to_ksh(user.balance),
                'total_pnl_usd': 0.0,
                'total_pnl_ksh': 0.0,
                'win_rate': 0.0,
                'wins': 0,
                'losses': 0,
                'largest_win_usd': 0.0,
                'largest_win_ksh': 0.0,
                'largest_loss_usd': 0.0,
                'largest_loss_ksh': 0.0,
                'last_trade': None,
                'trades_today': 0
            }
        
        # Calculate metrics
        total_pnl = sum(t.profit_loss for t in trades)
        wins = sum(1 for t in trades if t.profit_loss > 0)
        losses = sum(1 for t in trades if t.profit_loss < 0)
        win_rate = (wins / len(trades) * 100) if trades else 0
        
        wins_pnl = [t.profit_loss for t in trades if t.profit_loss > 0]
        losses_pnl = [t.profit_loss for t in trades if t.profit_loss < 0]
        
        largest_win = max(wins_pnl) if wins_pnl else 0.0
        largest_loss = min(losses_pnl) if losses_pnl else 0.0
        
        # Trades today
        today = datetime.utcnow().date()
        trades_today = sum(1 for t in trades if t.timestamp.date() == today)
        
        # Last trade
        last_trade = trades[-1] if trades else None
        
        return {
            'username': username,
            'total_trades': len(trades),
            'balance_usd': round(user.balance, 2),
            'balance_ksh': currency_converter.usd_to_ksh(user.balance),
            'total_pnl_usd': round(total_pnl, 2),
            'total_pnl_ksh': currency_converter.usd_to_ksh(total_pnl),
            'win_rate': round(win_rate, 2),
            'wins': wins,
            'losses': losses,
            'largest_win_usd': round(largest_win, 2),
            'largest_win_ksh': currency_converter.usd_to_ksh(largest_win),
            'largest_loss_usd': round(largest_loss, 2),
            'largest_loss_ksh': currency_converter.usd_to_ksh(largest_loss),
            'last_trade': {
                'pair': last_trade.pair,
                'amount_usd': round(last_trade.amount, 2),
                'amount_ksh': currency_converter.usd_to_ksh(last_trade.amount),
                'result': last_trade.result,
                'profit_loss_usd': round(last_trade.profit_loss, 2),
                'profit_loss_ksh': currency_converter.usd_to_ksh(last_trade.profit_loss),
                'timestamp': last_trade.timestamp.isoformat()
            } if last_trade else None,
            'trades_today': trades_today
        }
    
    @staticmethod
    def get_pair_realtime_stats(username, pair):
        """Get real-time stats for a specific pair"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        trades = Trade.query.filter_by(user_id=user.id, pair=pair).all()
        
        if not trades:
            return {
                'pair': pair,
                'total_trades': 0,
                'total_volume_usd': 0.0,
                'total_volume_ksh': 0.0,
                'total_pnl_usd': 0.0,
                'total_pnl_ksh': 0.0,
                'win_rate': 0.0,
                'avg_trade_size_usd': 0.0,
                'avg_trade_size_ksh': 0.0
            }
        
        total_pnl = sum(t.profit_loss for t in trades)
        total_volume = sum(t.amount for t in trades)
        wins = sum(1 for t in trades if t.profit_loss > 0)
        win_rate = (wins / len(trades) * 100) if trades else 0
        avg_trade_size = total_volume / len(trades) if trades else 0
        
        return {
            'pair': pair,
            'total_trades': len(trades),
            'total_volume_usd': round(total_volume, 2),
            'total_volume_ksh': currency_converter.usd_to_ksh(total_volume),
            'total_pnl_usd': round(total_pnl, 2),
            'total_pnl_ksh': currency_converter.usd_to_ksh(total_pnl),
            'win_rate': round(win_rate, 2),
            'avg_trade_size_usd': round(avg_trade_size, 2),
            'avg_trade_size_ksh': currency_converter.usd_to_ksh(avg_trade_size)
        }
    
    @staticmethod
    def get_platform_realtime_stats():
        """Get real-time platform stats"""
        users = User.query.all()
        all_trades = Trade.query.all()
        
        if not all_trades:
            return {
                'total_users': len(users),
                'total_trades': 0,
                'total_volume_usd': 0.0,
                'total_volume_ksh': 0.0,
                'total_pnl_usd': 0.0,
                'total_pnl_ksh': 0.0,
                'avg_trade_size_usd': 0.0,
                'avg_trade_size_ksh': 0.0,
                'exchange_rate': currency_converter.get_rate()
            }
        
        total_volume = sum(t.amount for t in all_trades)
        total_pnl = sum(t.profit_loss for t in all_trades)
        avg_trade_size = total_volume / len(all_trades) if all_trades else 0
        
        return {
            'total_users': len(users),
            'total_trades': len(all_trades),
            'total_volume_usd': round(total_volume, 2),
            'total_volume_ksh': currency_converter.usd_to_ksh(total_volume),
            'total_pnl_usd': round(total_pnl, 2),
            'total_pnl_ksh': currency_converter.usd_to_ksh(total_pnl),
            'avg_trade_size_usd': round(avg_trade_size, 2),
            'avg_trade_size_ksh': currency_converter.usd_to_ksh(avg_trade_size),
            'exchange_rate': currency_converter.get_rate()
        }
    
    @staticmethod
    def get_live_trade_stream(username, limit=20):
        """Get live trade stream for real-time display"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return []
        
        trades = Trade.query.filter_by(user_id=user.id)\
            .order_by(Trade.timestamp.desc())\
            .limit(limit).all()
        
        return [
            {
                'id': t.id,
                'pair': t.pair,
                'amount_usd': round(t.amount, 2),
                'amount_ksh': currency_converter.usd_to_ksh(t.amount),
                'result': t.result,
                'profit_loss_usd': round(t.profit_loss, 2),
                'profit_loss_ksh': currency_converter.usd_to_ksh(t.profit_loss),
                'timestamp': t.timestamp.isoformat(),
                'entry_price': t.entry_price,
                'exit_price': t.exit_price
            }
            for t in trades
        ]


# Global instance
realtime_analytics = RealtimeAnalytics()
