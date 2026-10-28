"""
Advanced Analytics Engine
Provides comprehensive trading analytics and performance metrics
"""
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Trade, User
from typing import Dict, List, Optional
import statistics


class AdvancedAnalytics:
    """Advanced analytics for user trading performance."""
    
    @staticmethod
    def calculate_win_rate(user_id: int) -> Dict:
        """
        Calculate user's win rate.
        
        Returns:
            Dict with wins, losses, win_rate percentage, and total trades
        """
        trades = Trade.query.filter_by(user_id=user_id).all()
        
        if not trades:
            return {
                'wins': 0,
                'losses': 0,
                'neutrals': 0,
                'total_trades': 0,
                'win_rate': 0.0,
                'loss_rate': 0.0
            }
        
        wins = sum(1 for t in trades if t.result == 'win' and t.profit_loss > 0)
        losses = sum(1 for t in trades if t.result == 'loss' and t.profit_loss < 0)
        neutrals = len(trades) - wins - losses
        
        total = len(trades)
        win_rate = (wins / total * 100) if total > 0 else 0
        loss_rate = (losses / total * 100) if total > 0 else 0
        
        return {
            'wins': wins,
            'losses': losses,
            'neutrals': neutrals,
            'total_trades': total,
            'win_rate': round(win_rate, 2),
            'loss_rate': round(loss_rate, 2)
        }
    
    @staticmethod
    def calculate_performance_metrics(user_id: int) -> Dict:
        """
        Calculate detailed performance metrics including Sharpe ratio and max drawdown.
        
        Returns:
            Dict with performance metrics
        """
        trades = Trade.query.filter_by(user_id=user_id).all()
        
        if not trades:
            return {
                'total_profit_loss': 0.0,
                'average_trade_profit': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'consecutive_wins': 0,
                'consecutive_losses': 0
            }
        
        # Basic metrics
        profit_losses = [t.profit_loss for t in trades]
        total_pl = sum(profit_losses)
        avg_pl = statistics.mean(profit_losses)
        
        wins_pl = [pl for pl in profit_losses if pl > 0]
        losses_pl = [pl for pl in profit_losses if pl < 0]
        
        largest_win = max(wins_pl) if wins_pl else 0.0
        largest_loss = min(losses_pl) if losses_pl else 0.0
        
        # Profit factor
        total_wins = sum(wins_pl) if wins_pl else 0
        total_losses = abs(sum(losses_pl)) if losses_pl else 0
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Sharpe ratio (simplified - using std dev of returns)
        try:
            std_dev = statistics.stdev(profit_losses)
            sharpe = (avg_pl / std_dev) if std_dev > 0 else 0
        except:
            sharpe = 0.0
        
        # Max drawdown
        cumulative = 0
        peak = 0
        max_dd = 0
        for pl in profit_losses:
            cumulative += pl
            peak = max(peak, cumulative)
            dd = peak - cumulative
            max_dd = max(max_dd, dd)
        
        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for t in trades:
            if t.profit_loss > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            elif t.profit_loss < 0:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        return {
            'total_profit_loss': round(total_pl, 2),
            'average_trade_profit': round(avg_pl, 2),
            'largest_win': round(largest_win, 2),
            'largest_loss': round(largest_loss, 2),
            'total_wins': round(total_wins, 2),
            'total_losses': round(total_losses, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown': round(max_dd, 2),
            'consecutive_wins': max_consecutive_wins,
            'consecutive_losses': max_consecutive_losses
        }
    
    @staticmethod
    def calculate_pair_statistics(user_id: int) -> Dict[str, Dict]:
        """
        Calculate performance metrics for each currency pair.
        
        Returns:
            Dict with statistics per pair
        """
        trades = Trade.query.filter_by(user_id=user_id).all()
        pair_data = {}
        
        for trade in trades:
            if trade.pair not in pair_data:
                pair_data[trade.pair] = {
                    'trades': 0,
                    'wins': 0,
                    'total_pl': 0.0,
                    'total_volume': 0.0
                }
            
            pair_data[trade.pair]['trades'] += 1
            pair_data[trade.pair]['total_pl'] += trade.profit_loss
            pair_data[trade.pair]['total_volume'] += trade.amount
            
            if trade.profit_loss > 0:
                pair_data[trade.pair]['wins'] += 1
        
        # Calculate statistics
        result = {}
        for pair, data in pair_data.items():
            win_rate = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
            avg_trade = (data['total_pl'] / data['trades']) if data['trades'] > 0 else 0
            
            result[pair] = {
                'trade_count': data['trades'],
                'wins': data['wins'],
                'win_rate': round(win_rate, 2),
                'total_profit_loss': round(data['total_pl'], 2),
                'average_trade_profit': round(avg_trade, 2),
                'total_volume': round(data['total_volume'], 2)
            }
        
        return result
    
    @staticmethod
    def calculate_time_period_statistics(
        user_id: int,
        period_days: int = 30
    ) -> Dict:
        """
        Calculate statistics for a specific time period.
        
        Args:
            user_id: User ID
            period_days: Number of days to look back
        
        Returns:
            Dict with period statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        trades = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.timestamp >= cutoff_date
        ).all()
        
        if not trades:
            return {
                'period_days': period_days,
                'trades': 0,
                'total_profit_loss': 0.0,
                'daily_average': 0.0,
                'winning_days': 0,
                'losing_days': 0
            }
        
        total_pl = sum(t.profit_loss for t in trades)
        
        # Group by day
        daily_data = {}
        for trade in trades:
            day = trade.timestamp.date()
            if day not in daily_data:
                daily_data[day] = 0.0
            daily_data[day] += trade.profit_loss
        
        winning_days = sum(1 for pl in daily_data.values() if pl > 0)
        losing_days = sum(1 for pl in daily_data.values() if pl < 0)
        
        daily_avg = (total_pl / len(daily_data)) if daily_data else 0
        
        return {
            'period_days': period_days,
            'trades': len(trades),
            'total_profit_loss': round(total_pl, 2),
            'daily_average': round(daily_avg, 2),
            'winning_days': winning_days,
            'losing_days': losing_days,
            'days_traded': len(daily_data)
        }
    
    @staticmethod
    def get_user_ranking(limit: int = 100) -> List[Dict]:
        """
        Get user leaderboard based on total profit/loss.
        
        Args:
            limit: Number of users to return
        
        Returns:
            List of users with their statistics
        """
        users = User.query.all()
        ranking_data = []
        
        for user in users:
            metrics = AdvancedAnalytics.calculate_performance_metrics(user.id)
            wr = AdvancedAnalytics.calculate_win_rate(user.id)
            
            ranking_data.append({
                'username': user.username,
                'balance': round(user.balance, 2),
                'total_profit_loss': metrics['total_profit_loss'],
                'win_rate': wr['win_rate'],
                'total_trades': wr['total_trades'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'profit_factor': metrics['profit_factor']
            })
        
        # Sort by total profit/loss
        ranking_data.sort(
            key=lambda x: x['total_profit_loss'],
            reverse=True
        )
        
        return ranking_data[:limit]
    
    @staticmethod
    def calculate_risk_metrics(user_id: int) -> Dict:
        """
        Calculate comprehensive risk metrics.
        
        Returns:
            Dict with risk metrics
        """
        metrics = AdvancedAnalytics.calculate_performance_metrics(user_id)
        wr = AdvancedAnalytics.calculate_win_rate(user_id)
        
        trades = Trade.query.filter_by(user_id=user_id).all()
        profit_losses = [t.profit_loss for t in trades]
        
        if not profit_losses:
            return {
                'volatility': 0.0,
                'value_at_risk_95': 0.0,
                'expected_shortfall': 0.0,
                'risk_reward_ratio': 0.0,
                'max_loss': 0.0
            }
        
        # Volatility (std dev)
        try:
            volatility = statistics.stdev(profit_losses)
        except:
            volatility = 0.0
        
        # Value at Risk (95% confidence)
        sorted_pl = sorted(profit_losses)
        var_index = int(len(sorted_pl) * 0.05)
        var_95 = sorted_pl[var_index] if var_index < len(sorted_pl) else sorted_pl[0]
        
        # Expected shortfall (average of worst 5%)
        worst_trades = sorted_pl[:var_index + 1]
        expected_shortfall = sum(worst_trades) / len(worst_trades) if worst_trades else 0
        
        # Risk/Reward ratio
        avg_win = statistics.mean([pl for pl in profit_losses if pl > 0]) if any(pl > 0 for pl in profit_losses) else 0
        avg_loss = statistics.mean([pl for pl in profit_losses if pl < 0]) if any(pl < 0 for pl in profit_losses) else 0
        risk_reward = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        max_loss = min(profit_losses)
        
        return {
            'volatility': round(volatility, 2),
            'value_at_risk_95': round(var_95, 2),
            'expected_shortfall': round(expected_shortfall, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'max_loss': round(max_loss, 2),
            'average_win': round(avg_win, 2),
            'average_loss': round(avg_loss, 2)
        }


# Create global instance
advanced_analytics = AdvancedAnalytics()
