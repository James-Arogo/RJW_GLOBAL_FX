import random
import math
from datetime import datetime
from typing import Dict, Tuple


class MarketEngine:
    """
    Realistic forex market simulation engine with:
    - Brownian motion for price simulation
    - Volatility tracking per pair
    - Bid-ask spreads
    - Price history for technical analysis
    """
    
    def __init__(self):
        # Base prices for currency pairs
        self.base_prices = {
            "EUR/USD": 1.10,
            "GBP/USD": 1.25,
            "USD/JPY": 145.20,
            "XAU/USD": 1980.50,
            "USD/CHF": 0.88,
            "AUD/USD": 0.65,
            "NZD/USD": 0.60,
            "USD/CAD": 1.35
        }
        
        self.prices = self.base_prices.copy()
        self.price_history = {pair: [price] for pair, price in self.base_prices.items()}
        
        # Volatility per pair (annualized)
        self.volatility = {
            "EUR/USD": 0.10,
            "GBP/USD": 0.12,
            "USD/JPY": 0.11,
            "XAU/USD": 0.15,
            "USD/CHF": 0.09,
            "AUD/USD": 0.13,
            "NZD/USD": 0.14,
            "USD/CAD": 0.10
        }
        
        # Bid-ask spreads (in pips, normalized to price decimal places)
        self.spreads = {
            "EUR/USD": 0.0002,
            "GBP/USD": 0.0003,
            "USD/JPY": 0.01,
            "XAU/USD": 0.50,
            "USD/CHF": 0.0002,
            "AUD/USD": 0.0003,
            "NZD/USD": 0.0004,
            "USD/CAD": 0.0003
        }
        
        # Trend bias (mean reversion)
        self.trend = {pair: 0.0 for pair in self.base_prices}
    
    def _brownian_motion(self, pair: str, dt: float = 1/252) -> float:
        """
        Generate price change using geometric Brownian motion.
        More realistic than random walk.
        
        Args:
            pair: Currency pair
            dt: Time step (default: 1 trading day)
        
        Returns:
            Price change
        """
        volatility = self.volatility.get(pair, 0.10)
        drift = 0.0001  # Small positive drift
        
        # Standard normal random variable
        z = random.gauss(0, 1)
        
        # Calculate price change using GBM
        price_change_percent = (drift * dt + volatility * math.sqrt(dt) * z) / 100
        return price_change_percent
    
    def get_prices(self) -> Dict[str, float]:
        """
        Get current prices with realistic movement using Brownian motion.
        
        Returns:
            Dict of current prices for all pairs
        """
        for pair in self.prices:
            # Calculate price change
            change_percent = self._brownian_motion(pair)
            price_change = self.prices[pair] * change_percent
            
            # Apply change with slight constraints
            self.prices[pair] += price_change
            
            # Keep price within reasonable range (mean reversion)
            base = self.base_prices[pair]
            max_deviation = base * 0.1  # 10% max deviation
            if self.prices[pair] < base - max_deviation:
                self.prices[pair] = base - max_deviation
            elif self.prices[pair] > base + max_deviation:
                self.prices[pair] = base + max_deviation
            
            # Round appropriately
            self.prices[pair] = round(self.prices[pair], 5)
            
            # Store in history
            if len(self.price_history[pair]) < 1000:
                self.price_history[pair].append(self.prices[pair])
        
        return self.prices.copy()
    
    def get_bid_ask(self, pair: str) -> Tuple[float, float]:
        """
        Get bid and ask prices with spread.
        
        Returns:
            Tuple of (bid_price, ask_price)
        """
        spread = self.spreads.get(pair, 0.0002)
        mid_price = self.prices.get(pair, 0)
        
        bid = round(mid_price - spread/2, 5)
        ask = round(mid_price + spread/2, 5)
        
        return bid, ask
    
    def execute_trade(self, pair: str, amount: float) -> Dict:
        """
        Execute a trade with realistic outcome.
        Outcome depends on price movement, volatility, and system margin.
        
        Args:
            pair: Currency pair
            amount: Trade amount in USD
        
        Returns:
            Trade result with profit/loss
        """
        # Get current bid/ask
        bid, ask = self.get_bid_ask(pair)
        entry_price = ask  # Buy at ask price
        
        # Simulate price movement during trade (0.5s to 2 minutes)
        time_window = random.uniform(0.5/1440, 2/1440)  # Minutes as fraction of day
        
        price_change_percent = self._brownian_motion(pair, time_window)
        exit_price = entry_price * (1 + price_change_percent)
        
        # Calculate raw P&L
        price_change = exit_price - entry_price
        raw_profit_loss = (price_change / entry_price) * amount
        
        # Apply system margin (30% for losing trades)
        if raw_profit_loss < 0:
            system_margin = 0.30
            raw_profit_loss = raw_profit_loss * (1 + system_margin)
        
        # Determine result
        if raw_profit_loss > 0:
            result = "win"
        elif raw_profit_loss < 0:
            result = "loss"
        else:
            result = "neutral"
        
        return {
            "pair": pair,
            "entry_price": round(entry_price, 5),
            "exit_price": round(exit_price, 5),
            "result": result,
            "profit_loss": round(raw_profit_loss, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "spread": round(self.spreads.get(pair, 0), 5)
        }
    
    def get_price_history(self, pair: str, limit: int = 100) -> list:
        """
        Get price history for a pair.
        
        Args:
            pair: Currency pair
            limit: Number of historical prices
        
        Returns:
            List of historical prices
        """
        history = self.price_history.get(pair, [])
        return history[-limit:]


# Global market engine instance
market_engine = MarketEngine()
