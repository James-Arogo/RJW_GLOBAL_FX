from datetime import datetime
from models import db, Order, Trade, User
from utils.market_engine import market_engine
from utils.profit_manager import profit_manager


class OrderManager:
    """Manages advanced trading orders (limit, stop-loss, take-profit)."""
    
    def __init__(self):
        self.active_orders = []
    
    def create_limit_order(self, user_id, pair, amount, target_price, order_type='limit'):
        """Create a limit order."""
        order = Order(
            user_id=user_id,
            pair=pair,
            amount=amount,
            order_type=order_type,
            price=target_price,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    def create_stop_loss_order(self, user_id, pair, amount, stop_price):
        """Create a stop-loss order."""
        return self.create_limit_order(user_id, pair, amount, stop_price, 'stop_loss')
    
    def create_take_profit_order(self, user_id, pair, amount, target_price):
        """Create a take-profit order."""
        return self.create_limit_order(user_id, pair, amount, target_price, 'take_profit')
    
    def check_pending_orders(self):
        """Check and execute pending orders based on current market prices."""
        current_prices = market_engine.get_prices()
        executed_orders = []
        
        pending_orders = Order.query.filter_by(status='pending').all()
        
        for order in pending_orders:
            current_price = current_prices.get(order.pair)
            if not current_price:
                continue
            
            should_execute = False
            
            if order.order_type == 'limit':
                # Buy limit: execute when price <= target
                # Sell limit: execute when price >= target
                should_execute = current_price <= order.price
            elif order.order_type == 'stop_loss':
                # Stop-loss: execute when price <= target (for long positions)
                should_execute = current_price <= order.price
            elif order.order_type == 'take_profit':
                # Take-profit: execute when price >= target (for long positions)
                should_execute = current_price >= order.price
            
            if should_execute:
                executed_trade = self._execute_order(order, current_price)
                if executed_trade:
                    executed_orders.append(executed_trade)
        
        return executed_orders
    
    def _execute_order(self, order, current_price):
        """Execute a pending order."""
        try:
            user = User.query.get(order.user_id)
            if not user or user.balance < order.amount:
                return None
            
            # Execute the trade at current price
            result = market_engine.execute_trade(order.pair, order.amount)
            result = profit_manager.enforce_margin(result)
            
            # Create trade record
            trade = Trade(
                user_id=user.id,
                pair=order.pair,
                amount=order.amount,
                result=result["result"],
                profit_loss=result["profit_loss"],
                trade_type=order.order_type,
                entry_price=current_price,
                status='executed'
            )
            
            # Update user balance
            user.balance += result["profit_loss"]
            
            # Update order status
            order.status = 'executed'
            order.executed_at = datetime.utcnow()
            
            db.session.add(trade)
            db.session.commit()
            
            return {
                'order_id': order.id,
                'trade_id': trade.id,
                'pair': order.pair,
                'amount': order.amount,
                'execution_price': current_price,
                'profit_loss': result["profit_loss"]
            }
            
        except Exception as e:
            print(f"Error executing order {order.id}: {e}")
            return None
    
    def cancel_order(self, order_id, user_id):
        """Cancel a pending order."""
        order = Order.query.filter_by(id=order_id, user_id=user_id, status='pending').first()
        if order:
            order.status = 'cancelled'
            db.session.commit()
            return True
        return False
    
    def get_user_orders(self, user_id, status=None):
        """Get user's orders, optionally filtered by status."""
        query = Order.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Order.created_at.desc()).all()
    
    def get_order_statistics(self, user_id):
        """Get order execution statistics for a user."""
        orders = Order.query.filter_by(user_id=user_id).all()
        
        total_orders = len(orders)
        executed_orders = len([o for o in orders if o.status == 'executed'])
        cancelled_orders = len([o for o in orders if o.status == 'cancelled'])
        pending_orders = len([o for o in orders if o.status == 'pending'])
        
        execution_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'executed_orders': executed_orders,
            'cancelled_orders': cancelled_orders,
            'pending_orders': pending_orders,
            'execution_rate': round(execution_rate, 2)
        }


# Global order manager instance
order_manager = OrderManager()
