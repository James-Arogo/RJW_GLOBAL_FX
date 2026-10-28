"""
Live Price Simulation Engine for Forex Trading
Realistic real-time price movements with market dynamics
Optimized for student trading platform
"""

import random
import math
from datetime import datetime, timedelta
from collections import deque


class LivePriceEngine:
    """Generate realistic real-time forex prices with market dynamics"""
    
    def __init__(self):
        """Initialize price engine with base prices and volatility"""
        
        # Base prices at startup (realistic market rates)
        self.base_prices = {
            'EUR/USD': 1.0850,
            'GBP/USD': 1.2750,
            'USD/JPY': 149.50,
            'USD/CHF': 0.8850,
            'AUD/USD': 0.6550,
            'USD/CAD': 1.3250,
            'XAU/USD': 2050.00,  # Gold
            'BTC/USD': 42500.00,  # Bitcoin (crypto-like)
        }
        
        # Volatility factors for each pair (higher = more movement)
        self.volatility = {
            'EUR/USD': 0.0008,
            'GBP/USD': 0.0012,
            'USD/JPY': 0.0015,
            'USD/CHF': 0.0010,
            'AUD/USD': 0.0014,
            'USD/CAD': 0.0009,
            'XAU/USD': 0.0020,
            'BTC/USD': 0.0050,  # High volatility
        }
        
        # Trend directions (can change)
        self.trends = {pair: random.choice([1, -1]) for pair in self.base_prices}
        
        # Current prices
        self.current_prices = self.base_prices.copy()
        
        # Price history for charting (keep last 100 updates)
        self.price_history = {
            pair: deque(maxlen=100) for pair in self.base_prices
        }
        
        # Last update timestamp
        self.last_update = datetime.utcnow()
        
        # Market state (for realistic trading hours simulation)
        self.is_market_open = True
        
        # Initialize price history
        for pair in self.base_prices:
            self.price_history[pair].append({
                'timestamp': datetime.utcnow().isoformat(),
                'price': self.base_prices[pair],
                'change': 0,
                'change_percent': 0
            })
    
    def update_prices(self):
        """Update all prices with realistic market movement"""
        
        new_prices = {}
        
        for pair, base_price in self.base_prices.items():
            # Random walk with drift (trend)
            random_component = random.gauss(0, 1) * self.volatility[pair]
            trend_component = self.trends[pair] * 0.00001
            
            # Occasional trend reversals (realistic market behavior)
            if random.random() < 0.01:  # 1% chance per update
                self.trends[pair] *= -1
            
            # Mean reversion (price tends to move back to average)
            mean_reversion = (self.base_prices[pair] - self.current_prices[pair]) * 0.0001
            
            # Calculate new price
            price_change = random_component + trend_component + mean_reversion
            new_price = self.current_prices[pair] * (1 + price_change)
            
            # Keep price realistic (not too far from base)
            max_deviation = self.base_prices[pair] * 0.05  # ±5%
            new_price = max(
                self.base_prices[pair] - max_deviation,
                min(self.base_prices[pair] + max_deviation, new_price)
            )
            
            new_prices[pair] = round(new_price, 4)
        
        # Update current prices
        old_prices = self.current_prices.copy()
        self.current_prices = new_prices
        
        # Record in history
        for pair in self.base_prices:
            change = self.current_prices[pair] - old_prices[pair]
            change_percent = (change / old_prices[pair]) * 100 if old_prices[pair] > 0 else 0
            
            self.price_history[pair].append({
                'timestamp': datetime.utcnow().isoformat(),
                'price': self.current_prices[pair],
                'change': round(change, 6),
                'change_percent': round(change_percent, 4)
            })
        
        self.last_update = datetime.utcnow()
        return self.current_prices
    
    def get_current_prices(self):
        """Get all current prices"""
        return {
            pair: {
                'price': self.current_prices[pair],
                'bid': round(self.current_prices[pair] - 0.0001, 4),
                'ask': round(self.current_prices[pair] + 0.0001, 4),
                'change': round(
                    self.current_prices[pair] - self.base_prices[pair], 6
                ),
                'change_percent': round(
                    ((self.current_prices[pair] - self.base_prices[pair]) / 
                     self.base_prices[pair]) * 100, 2
                ),
                'timestamp': self.last_update.isoformat()
            }
            for pair in self.base_prices
        }
    
    def get_price_history(self, pair, limit=50):
        """Get price history for charting"""
        if pair not in self.price_history:
            return []
        
        history = list(self.price_history[pair])[-limit:]
        return history
    
    def get_pair_volatility(self, pair):
        """Get volatility index for a pair"""
        if pair not in self.price_history:
            return 0
        
        history = list(self.price_history[pair])[-20:]
        if len(history) < 2:
            return 0
        
        prices = [h['price'] for h in history]
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        volatility = math.sqrt(variance)
        
        return round(volatility, 6)
    
    def get_market_sentiment(self):
        """Analyze overall market sentiment"""
        gainers = 0
        losers = 0
        
        for pair in self.base_prices:
            change = self.current_prices[pair] - self.base_prices[pair]
            if change > 0:
                gainers += 1
            elif change < 0:
                losers += 1
        
        total = gainers + losers
        bullish_percent = (gainers / total * 100) if total > 0 else 50
        
        if bullish_percent >= 60:
            sentiment = 'BULLISH'
        elif bullish_percent <= 40:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'sentiment': sentiment,
            'bullish_percent': round(bullish_percent, 2),
            'gainers': gainers,
            'losers': losers,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def simulate_market_hours(self):
        """Simulate realistic market open/close times (Kenya timezone)"""
        # Markets are typically open Mon-Fri, but we'll keep it simple for student platform
        # Just keep it always open for the simulation
        self.is_market_open = True
        return self.is_market_open
    
    def reset_prices(self):
        """Reset prices to base (for testing)"""
        self.current_prices = self.base_prices.copy()
        self.trends = {pair: random.choice([1, -1]) for pair in self.base_prices}
        self.price_history = {
            pair: deque(maxlen=100) for pair in self.base_prices
        }
        for pair in self.base_prices:
            self.price_history[pair].append({
                'timestamp': datetime.utcnow().isoformat(),
                'price': self.base_prices[pair],
                'change': 0,
                'change_percent': 0
            })


# Global instance
live_price_engine = LivePriceEngine()
