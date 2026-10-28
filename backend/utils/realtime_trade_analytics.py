"""
Enhanced Real-time Trade Analytics Engine
Provides live trade metrics, streaming updates, and advanced analytics
"""

from datetime import datetime, timedelta
from collections import defaultdict
from models import db, Trade, User
from utils.currency_converter import currency_converter
import json


class RealtimeTradeAnalytics:
    """Advanced real-time analytics for live trade monitoring"""
    
    def __init__(self):
        self.trade_cache = {}
        self.user_metrics = {}
        self.market_metrics = {}
    
    # ========== USER REAL-TIME METRICS ==========
    
    @staticmethod
    def get_live_user_metrics(username):
        """Get real-time user trading metrics"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        trades = Trade.query.filter_by(user_id=user.id).all()
        
        if not trades:
            return {
                'username': username,
                'balance': round(user.balance, 2),
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'wins': 0,
                'losses': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'daily_pnl': 0.0,
                'trades_today': 0,
                'avg_trade_duration_minutes': 0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'win_loss_ratio': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Calculate core metrics
        total_pnl = sum(t.profit_loss for t in trades)
        wins = [t for t in trades if t.profit_loss > 0]
        losses = [t for t in trades if t.profit_loss < 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / len(trades) * 100) if trades else 0
        
        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        if trades:
            for t in reversed(trades):
                if t.profit_loss > 0:
                    consecutive_wins += 1
                else:
                    break
            for t in reversed(trades):
                if t.profit_loss < 0:
                    consecutive_losses += 1
                else:
                    break
        
        # Profit factor
        total_wins = sum(t.profit_loss for t in wins)
        total_losses = abs(sum(t.profit_loss for t in losses))
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Average profit and loss
        avg_profit = (total_wins / len(wins)) if wins else 0
        avg_loss = (total_losses / len(losses)) if losses else 0
        
        # Daily metrics
        today = datetime.utcnow().date()
        today_trades = [t for t in trades if t.timestamp.date() == today]
        daily_pnl = sum(t.profit_loss for t in today_trades)
        
        # Average trade duration
        trade_durations = []
        for t in trades:
            if hasattr(t, 'exit_time') and t.exit_time and hasattr(t, 'entry_time') and t.entry_time:
                duration = (t.exit_time - t.entry_time).total_seconds() / 60
                trade_durations.append(duration)
        avg_duration = sum(trade_durations) / len(trade_durations) if trade_durations else 0
        
        # Largest win/loss
        largest_win = max([t.profit_loss for t in wins]) if wins else 0
        largest_loss = abs(min([t.profit_loss for t in losses])) if losses else 0
        
        # Win/Loss ratio
        win_loss_ratio = win_count / loss_count if loss_count > 0 else (win_count if win_count > 0 else 0)
        
        return {
            'username': username,
            'balance': round(user.balance, 2),
            'total_trades': len(trades),
            'total_pnl': round(total_pnl, 2),
            'win_rate': round(win_rate, 2),
            'wins': win_count,
            'losses': loss_count,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses,
            'avg_profit': round(avg_profit, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'daily_pnl': round(daily_pnl, 2),
            'trades_today': len(today_trades),
            'avg_trade_duration_minutes': round(avg_duration, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'win_loss_ratio': round(win_loss_ratio, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========== PAIR-SPECIFIC REAL-TIME METRICS ==========
    
    @staticmethod
    def get_live_pair_metrics(username, pair):
        """Get real-time metrics for a specific currency pair"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        trades = Trade.query.filter_by(user_id=user.id, pair=pair).all()
        
        if not trades:
            return {
                'pair': pair,
                'total_trades': 0,
                'total_volume': 0.0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'wins': 0,
                'losses': 0,
                'avg_trade_size': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        total_pnl = sum(t.profit_loss for t in trades)
        total_volume = sum(t.amount for t in trades)
        wins = [t for t in trades if t.profit_loss > 0]
        losses = [t for t in trades if t.profit_loss < 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / len(trades) * 100) if trades else 0
        avg_trade_size = total_volume / len(trades) if trades else 0
        
        best_trade = max([t.profit_loss for t in trades]) if trades else 0
        worst_trade = min([t.profit_loss for t in trades]) if trades else 0
        
        return {
            'pair': pair,
            'total_trades': len(trades),
            'total_volume': round(total_volume, 2),
            'total_pnl': round(total_pnl, 2),
            'win_rate': round(win_rate, 2),
            'wins': win_count,
            'losses': loss_count,
            'avg_trade_size': round(avg_trade_size, 2),
            'best_trade': round(best_trade, 2),
            'worst_trade': round(worst_trade, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========== LIVE TRADE STREAM ==========
    
    @staticmethod
    def get_live_trade_stream(username, limit=50):
        """Get live stream of recent trades for real-time display"""
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
                'amount': round(t.amount, 2),
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'pnl': round(t.profit_loss, 2),
                'result': t.result,
                'status': t.status,
                'timestamp': t.timestamp.isoformat(),
                'pnl_percent': round((t.profit_loss / t.amount * 100), 2) if t.amount > 0 else 0
            }
            for t in trades
        ]
    
    # ========== PLATFORM REAL-TIME METRICS ==========
    
    @staticmethod
    def get_live_platform_metrics():
        """Get real-time platform-wide metrics"""
        users = User.query.all()
        all_trades = Trade.query.all()
        
        if not users:
            return {
                'total_users': 0,
                'active_traders': 0,
                'total_trades': 0,
                'total_volume': 0.0,
                'total_platform_pnl': 0.0,
                'avg_win_rate': 0.0,
                'trades_today': 0,
                'active_pairs': [],
                'timestamp': datetime.utcnow().isoformat()
            }
        
        today = datetime.utcnow().date()
        today_trades = [t for t in all_trades if t.timestamp.date() == today]
        
        # Active traders (traders with at least one trade today)
        active_traders = set(t.user_id for t in today_trades)
        
        # Get all active pairs
        active_pairs = list(set(t.pair for t in all_trades))
        
        # Total metrics
        total_volume = sum(t.amount for t in all_trades)
        total_pnl = sum(t.profit_loss for t in all_trades)
        total_wins = sum(1 for t in all_trades if t.result == 'win')
        
        avg_win_rate = (total_wins / len(all_trades) * 100) if all_trades else 0
        
        return {
            'total_users': len(users),
            'active_traders': len(active_traders),
            'total_trades': len(all_trades),
            'total_volume': round(total_volume, 2),
            'total_platform_pnl': round(total_pnl, 2),
            'avg_win_rate': round(avg_win_rate, 2),
            'trades_today': len(today_trades),
            'active_pairs': sorted(active_pairs),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========== PERFORMANCE TRENDS ==========
    
    @staticmethod
    def get_performance_trend(username, timeframe_minutes=60):
        """Get performance trend data for charting"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return []
        
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=timeframe_minutes)
        
        trades = Trade.query.filter(
            Trade.user_id == user.id,
            Trade.timestamp >= start_time
        ).order_by(Trade.timestamp.asc()).all()
        
        if not trades:
            return []
        
        # Group trades by 5-minute intervals
        trend_data = []
        cumulative_pnl = 0
        
        for trade in trades:
            cumulative_pnl += trade.profit_loss
            trend_data.append({
                'timestamp': trade.timestamp.isoformat(),
                'pnl': round(cumulative_pnl, 2),
                'trade_count': len([t for t in trades if t.timestamp <= trade.timestamp]),
                'pair': trade.pair
            })
        
        return trend_data
    
    # ========== RISK METRICS ==========
    
    @staticmethod
    def get_live_risk_metrics(username):
        """Get real-time risk assessment metrics"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        
        trades = Trade.query.filter_by(user_id=user.id).all()
        
        if not trades:
            return {
                'max_drawdown': 0.0,
                'drawdown_percent': 0.0,
                'daily_loss_limit': 0.0,
                'daily_loss_used': 0.0,
                'risk_level': 'low',
                'position_size_risk': 'normal',
                'volatility_index': 0.0,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Calculate max drawdown
        cumulative_returns = [0]
        for trade in trades:
            cumulative_returns.append(cumulative_returns[-1] + trade.profit_loss)
        
        max_cumulative = max(cumulative_returns)
        max_drawdown = min(max_cumulative - ret for ret in cumulative_returns)
        drawdown_percent = (max_drawdown / max_cumulative * 100) if max_cumulative > 0 else 0
        
        # Daily loss metrics
        today = datetime.utcnow().date()
        today_trades = [t for t in trades if t.timestamp.date() == today]
        daily_loss = sum(t.profit_loss for t in today_trades if t.profit_loss < 0)
        daily_loss_limit = user.balance * 0.10  # 10% of balance
        
        # Risk level assessment
        if drawdown_percent > 30:
            risk_level = 'high'
        elif drawdown_percent > 15:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Position size risk
        avg_position = sum(t.amount for t in trades) / len(trades) if trades else 0
        position_percent = (avg_position / user.balance * 100) if user.balance > 0 else 0
        
        if position_percent > 20:
            position_size_risk = 'high'
        elif position_percent > 10:
            position_size_risk = 'medium'
        else:
            position_size_risk = 'normal'
        
        # Volatility index (standard deviation of PnL)
        pnl_values = [t.profit_loss for t in trades]
        if len(pnl_values) > 1:
            mean_pnl = sum(pnl_values) / len(pnl_values)
            variance = sum((x - mean_pnl) ** 2 for x in pnl_values) / len(pnl_values)
            volatility = variance ** 0.5
        else:
            volatility = 0.0
        
        return {
            'max_drawdown': round(max_drawdown, 2),
            'drawdown_percent': round(drawdown_percent, 2),
            'daily_loss_limit': round(daily_loss_limit, 2),
            'daily_loss_used': round(abs(daily_loss), 2),
            'daily_loss_remaining': round(daily_loss_limit + daily_loss, 2),
            'risk_level': risk_level,
            'position_size_risk': position_size_risk,
            'volatility_index': round(volatility, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # ========== PAIR COMPARISON ==========
    
    @staticmethod
    def get_pair_comparison(username):
        """Get comparative performance across all pairs"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return []
        
        trades = Trade.query.filter_by(user_id=user.id).all()
        
        # Group by pair
        pair_stats = defaultdict(lambda: {
            'trades': [],
            'wins': 0,
            'losses': 0,
            'total_pnl': 0
        })
        
        for trade in trades:
            pair_stats[trade.pair]['trades'].append(trade)
            pair_stats[trade.pair]['total_pnl'] += trade.profit_loss
            if trade.profit_loss > 0:
                pair_stats[trade.pair]['wins'] += 1
            else:
                pair_stats[trade.pair]['losses'] += 1
        
        # Format for comparison
        comparison = []
        for pair, stats in pair_stats.items():
            total_trades = len(stats['trades'])
            win_rate = (stats['wins'] / total_trades * 100) if total_trades > 0 else 0
            
            comparison.append({
                'pair': pair,
                'total_trades': total_trades,
                'total_pnl': round(stats['total_pnl'], 2),
                'win_rate': round(win_rate, 2),
                'wins': stats['wins'],
                'losses': stats['losses'],
                'avg_trade_size': round(sum(t.amount for t in stats['trades']) / total_trades, 2) if total_trades > 0 else 0
            })
        
        # Sort by total PnL descending
        comparison.sort(key=lambda x: x['total_pnl'], reverse=True)
        
        return comparison
    
    # ========== TIME-BASED ANALYTICS ==========
    
    @staticmethod
    def get_hourly_performance(username, days=7):
        """Get hourly performance breakdown"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return {}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        trades = Trade.query.filter(
            Trade.user_id == user.id,
            Trade.timestamp >= start_date
        ).all()
        
        # Group by hour
        hourly_data = defaultdict(lambda: {'trades': 0, 'pnl': 0.0, 'wins': 0})
        
        for trade in trades:
            hour = trade.timestamp.strftime('%H:00')
            hourly_data[hour]['trades'] += 1
            hourly_data[hour]['pnl'] += trade.profit_loss
            if trade.profit_loss > 0:
                hourly_data[hour]['wins'] += 1
        
        # Format for display
        formatted = []
        for hour in sorted(hourly_data.keys()):
            data = hourly_data[hour]
            win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            formatted.append({
                'hour': hour,
                'total_trades': data['trades'],
                'total_pnl': round(data['pnl'], 2),
                'wins': data['wins'],
                'win_rate': round(win_rate, 2),
                'avg_pnl': round(data['pnl'] / data['trades'], 2) if data['trades'] > 0 else 0
            })
        
        return formatted
    
    # ========== EXPORT METRICS ==========
    
    @staticmethod
    def get_complete_realtime_dashboard(username):
        """Get complete realtime dashboard data"""
        user_metrics = RealtimeTradeAnalytics.get_live_user_metrics(username)
        if not user_metrics:
            return None
        
        platform_metrics = RealtimeTradeAnalytics.get_live_platform_metrics()
        risk_metrics = RealtimeTradeAnalytics.get_live_risk_metrics(username)
        pair_comparison = RealtimeTradeAnalytics.get_pair_comparison(username)
        trade_stream = RealtimeTradeAnalytics.get_live_trade_stream(username, limit=20)
        
        return {
            'user_metrics': user_metrics,
            'risk_metrics': risk_metrics,
            'platform_metrics': platform_metrics,
            'pair_comparison': pair_comparison,
            'recent_trades': trade_stream,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global instance
realtime_trade_analytics = RealtimeTradeAnalytics()
