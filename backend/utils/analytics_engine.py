from datetime import datetime, timedelta
from models import db, Trade, User, Order
from sqlalchemy import func, and_
import calendar


class AnalyticsEngine:
    """Comprehensive analytics engine for trading data and user behavior."""
    
    def get_user_performance_metrics(self, user_id, days=30):
        """Get comprehensive performance metrics for a user."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        trades = Trade.query.filter(
            and_(
                Trade.user_id == user_id,
                Trade.timestamp >= start_date,
                Trade.status == 'executed'
            )
        ).all()
        
        if not trades:
            return self._empty_metrics()
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.result == 'win'])
        losing_trades = len([t for t in trades if t.result == 'loss'])
        neutral_trades = len([t for t in trades if t.result == 'neutral'])
        
        # Financial metrics
        total_profit_loss = sum(t.profit_loss for t in trades)
        total_amount_traded = sum(t.amount for t in trades)
        avg_trade_size = total_amount_traded / total_trades
        
        # Performance metrics
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        profit_factor = self._calculate_profit_factor(trades)
        max_drawdown = self._calculate_max_drawdown(trades)
        sharpe_ratio = self._calculate_sharpe_ratio(trades)
        
        # Best and worst trades
        best_trade = max(trades, key=lambda t: t.profit_loss)
        worst_trade = min(trades, key=lambda t: t.profit_loss)
        
        # Daily performance
        daily_performance = self._get_daily_performance(trades)
        
        # Currency pair performance
        pair_performance = self._get_pair_performance(trades)
        
        return {
            'period_days': days,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'neutral_trades': neutral_trades,
            'win_rate': round(win_rate, 2),
            'total_profit_loss': round(total_profit_loss, 2),
            'total_amount_traded': round(total_amount_traded, 2),
            'avg_trade_size': round(avg_trade_size, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'best_trade': {
                'pair': best_trade.pair,
                'profit_loss': best_trade.profit_loss,
                'date': best_trade.timestamp.isoformat()
            },
            'worst_trade': {
                'pair': worst_trade.pair,
                'profit_loss': worst_trade.profit_loss,
                'date': worst_trade.timestamp.isoformat()
            },
            'daily_performance': daily_performance,
            'pair_performance': pair_performance
        }
    
    def get_platform_statistics(self):
        """Get platform-wide statistics."""
        total_users = User.query.count()
        total_trades = Trade.query.count()
        total_orders = Order.query.count()
        
        # Active users (traded in last 7 days)
        active_users = Trade.query.filter(
            Trade.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).distinct(Trade.user_id).count()
        
        # Platform profit
        total_profit_loss = db.session.query(func.sum(Trade.profit_loss)).scalar() or 0
        platform_profit = abs(total_profit_loss) * 0.3  # 30% margin
        
        # User distribution by balance
        balance_distribution = self._get_balance_distribution()
        
        # Trading volume by pair
        volume_by_pair = self._get_volume_by_pair()
        
        # Recent activity
        recent_trades = Trade.query.order_by(Trade.timestamp.desc()).limit(10).all()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_trades': total_trades,
            'total_orders': total_orders,
            'platform_profit': round(platform_profit, 2),
            'balance_distribution': balance_distribution,
            'volume_by_pair': volume_by_pair,
            'recent_activity': [{
                'username': trade.user.username,
                'pair': trade.pair,
                'result': trade.result,
                'profit_loss': trade.profit_loss,
                'timestamp': trade.timestamp.isoformat()
            } for trade in recent_trades]
        }
    
    def get_market_sentiment(self):
        """Analyze market sentiment based on recent trades."""
        recent_trades = Trade.query.filter(
            Trade.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        if not recent_trades:
            return {'sentiment': 'neutral', 'confidence': 0}
        
        # Analyze by currency pair
        pair_sentiment = {}
        for trade in recent_trades:
            if trade.pair not in pair_sentiment:
                pair_sentiment[trade.pair] = {'wins': 0, 'losses': 0, 'total': 0}
            
            pair_sentiment[trade.pair]['total'] += 1
            if trade.result == 'win':
                pair_sentiment[trade.pair]['wins'] += 1
            elif trade.result == 'loss':
                pair_sentiment[trade.pair]['losses'] += 1
        
        # Calculate sentiment scores
        for pair in pair_sentiment:
            data = pair_sentiment[pair]
            if data['total'] > 0:
                win_rate = data['wins'] / data['total']
                if win_rate > 0.6:
                    sentiment = 'bullish'
                elif win_rate < 0.4:
                    sentiment = 'bearish'
                else:
                    sentiment = 'neutral'
                
                pair_sentiment[pair]['sentiment'] = sentiment
                pair_sentiment[pair]['confidence'] = min(data['total'] / 10, 1.0)  # Max confidence at 10+ trades
        
        return pair_sentiment
    
    def get_risk_metrics(self, user_id):
        """Calculate risk metrics for a user."""
        trades = Trade.query.filter_by(user_id=user_id).all()
        
        if len(trades) < 10:
            return {'error': 'Insufficient trade data for risk analysis'}
        
        # Value at Risk (VaR) calculation
        profit_losses = [t.profit_loss for t in trades]
        profit_losses.sort()
        
        # 95% VaR (5th percentile)
        var_95 = profit_losses[int(len(profit_losses) * 0.05)]
        
        # Maximum consecutive losses
        max_consecutive_losses = self._calculate_max_consecutive_losses(trades)
        
        # Average loss per losing trade
        losing_trades = [t for t in trades if t.result == 'loss']
        avg_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Risk of ruin (simplified)
        current_balance = User.query.get(user_id).balance
        avg_win = sum(t.profit_loss for t in trades if t.result == 'win') / len([t for t in trades if t.result == 'win']) if any(t.result == 'win' for t in trades) else 0
        win_rate = len([t for t in trades if t.result == 'win']) / len(trades)
        
        risk_of_ruin = self._calculate_risk_of_ruin(current_balance, avg_win, avg_loss, win_rate)
        
        return {
            'var_95': round(var_95, 2),
            'max_consecutive_losses': max_consecutive_losses,
            'avg_loss_per_trade': round(avg_loss, 2),
            'risk_of_ruin': round(risk_of_ruin, 4),
            'risk_level': self._assess_risk_level(risk_of_ruin)
        }
    
    def _empty_metrics(self):
        """Return empty metrics structure."""
        return {
            'period_days': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'neutral_trades': 0,
            'win_rate': 0,
            'total_profit_loss': 0,
            'total_amount_traded': 0,
            'avg_trade_size': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'daily_performance': {},
            'pair_performance': {}
        }
    
    def _calculate_profit_factor(self, trades):
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(t.profit_loss for t in trades if t.profit_loss > 0)
        gross_loss = abs(sum(t.profit_loss for t in trades if t.profit_loss < 0))
        return gross_profit / gross_loss if gross_loss > 0 else 0
    
    def _calculate_max_drawdown(self, trades):
        """Calculate maximum drawdown."""
        if not trades:
            return 0
        
        trades_sorted = sorted(trades, key=lambda t: t.timestamp)
        peak = 0
        max_drawdown = 0
        running_total = 0
        
        for trade in trades_sorted:
            running_total += trade.profit_loss
            if running_total > peak:
                peak = running_total
            drawdown = peak - running_total
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, trades):
        """Calculate Sharpe ratio (simplified)."""
        if len(trades) < 2:
            return 0
        
        returns = [t.profit_loss for t in trades]
        avg_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        return avg_return / std_dev if std_dev > 0 else 0
    
    def _get_daily_performance(self, trades):
        """Group trades by day."""
        daily = {}
        for trade in trades:
            date = trade.timestamp.date().isoformat()
            if date not in daily:
                daily[date] = {'trades': 0, 'profit_loss': 0, 'wins': 0}
            
            daily[date]['trades'] += 1
            daily[date]['profit_loss'] += trade.profit_loss
            if trade.result == 'win':
                daily[date]['wins'] += 1
        
        return daily
    
    def _get_pair_performance(self, trades):
        """Group trades by currency pair."""
        pairs = {}
        for trade in trades:
            if trade.pair not in pairs:
                pairs[trade.pair] = {'trades': 0, 'profit_loss': 0, 'wins': 0}
            
            pairs[trade.pair]['trades'] += 1
            pairs[trade.pair]['profit_loss'] += trade.profit_loss
            if trade.result == 'win':
                pairs[trade.pair]['wins'] += 1
        
        # Calculate win rates
        for pair in pairs:
            data = pairs[pair]
            data['win_rate'] = (data['wins'] / data['trades'] * 100) if data['trades'] > 0 else 0
        
        return pairs
    
    def _get_balance_distribution(self):
        """Get distribution of user balances."""
        users = User.query.all()
        ranges = {
            '0-100': 0, '100-500': 0, '500-1000': 0,
            '1000-5000': 0, '5000+': 0
        }
        
        for user in users:
            balance = user.balance
            if balance < 100:
                ranges['0-100'] += 1
            elif balance < 500:
                ranges['100-500'] += 1
            elif balance < 1000:
                ranges['500-1000'] += 1
            elif balance < 5000:
                ranges['1000-5000'] += 1
            else:
                ranges['5000+'] += 1
        
        return ranges
    
    def _get_volume_by_pair(self):
        """Get trading volume by currency pair."""
        volume = db.session.query(
            Trade.pair,
            func.sum(Trade.amount).label('total_volume'),
            func.count(Trade.id).label('trade_count')
        ).group_by(Trade.pair).all()
        
        return {
            row.pair: {
                'volume': round(row.total_volume, 2),
                'count': row.trade_count
            } for row in volume
        }
    
    def _calculate_max_consecutive_losses(self, trades):
        """Calculate maximum consecutive losses."""
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in sorted(trades, key=lambda t: t.timestamp):
            if trade.result == 'loss':
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_risk_of_ruin(self, balance, avg_win, avg_loss, win_rate):
        """Simplified risk of ruin calculation."""
        if avg_loss == 0:
            return 0
        
        # Kelly criterion approximation
        kelly = (win_rate * avg_win - (1 - win_rate) * abs(avg_loss)) / abs(avg_loss)
        
        # Risk of ruin approximation
        if kelly <= 0:
            return 1.0  # Certain ruin
        
        # Simplified calculation
        return ((1 - win_rate) / win_rate) ** (balance / abs(avg_loss))
    
    def _assess_risk_level(self, risk_of_ruin):
        """Assess risk level based on risk of ruin."""
        if risk_of_ruin < 0.01:
            return 'Very Low'
        elif risk_of_ruin < 0.05:
            return 'Low'
        elif risk_of_ruin < 0.15:
            return 'Medium'
        elif risk_of_ruin < 0.30:
            return 'High'
        else:
            return 'Very High'


# Global analytics engine instance
analytics_engine = AnalyticsEngine()
