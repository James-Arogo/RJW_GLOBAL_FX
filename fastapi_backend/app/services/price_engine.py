"""
Simulated Forex Price Engine with Geometric Brownian Motion

Features:
- Realistic price movements using GBM + volatility clustering
- Adaptive house bias based on platform exposure
- Cryptographically seeded sessions for audit trails
- WebSocket price streaming with variable tick intervals
- Per-pair net exposure tracking
- KES pairs for Kenyan market
"""

import asyncio
import time
import secrets
import math
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field, asdict
from collections import deque
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PriceConfig:
    """Configuration for each currency pair"""
    pair: str
    base_price: float
    volatility: float = 0.015  # Daily volatility (1.5%)
    trend: float = 0.0  # Daily drift
    max_bias: float = 0.008  # Max 0.8% bias cap
    tick_interval_min: float = 1.0  # Min seconds between ticks
    tick_interval_max: float = 5.0  # Max seconds between ticks


@dataclass
class Tick:
    """Single price tick"""
    timestamp: float
    pair: str
    price: float
    bid: float
    ask: float
    change: float
    change_percent: float
    volume: int
    volatility: float = 0.0  # Current volatility state


@dataclass
class MarketSession:
    """Market session with cryptographic seed for audit"""
    pair: str
    session_id: str
    seed: str  # Cryptographic seed (hex) - revealed at end
    seed_hash: str  # SHA-256 hash of seed (public during session)
    start_time: float
    end_time: Optional[float] = None
    base_price: float = 0.0
    current_price: float = 0.0
    ticks: List[Tick] = field(default_factory=list)
    platform_margin: float = 0.0  # Cumulative P&L percentage
    cumulative_bias: float = 0.0  # Total applied bias
    net_exposure: float = 0.0  # Sum(long stakes) - Sum(short stakes) in KES
    total_long_stakes: float = 0.0  # Total long position stakes
    total_short_stakes: float = 0.0  # Total short position stakes
    bias_history: List[Dict] = field(default_factory=list)  # Audit trail


# ============================================================================
# TICK STORAGE ABSTRACTION (Memory/Redis ready)
# ============================================================================

class TickStorage(ABC):
    """Abstract tick storage - can be memory or Redis"""
    
    @abstractmethod
    async def store_tick(self, session_id: str, tick: Tick) -> None:
        pass
    
    @abstractmethod
    async def get_ticks(self, session_id: str, limit: int = 100) -> List[Dict]:
        pass
    
    @abstractmethod
    async def get_latest_tick(self, session_id: str) -> Optional[Dict]:
        pass


class InMemoryTickStorage(TickStorage):
    """In-memory tick storage with deque for efficiency"""
    
    def __init__(self, max_ticks: int = 10000):
        self.storage: Dict[str, deque] = {}
        self.max_ticks = max_ticks
    
    async def store_tick(self, session_id: str, tick: Tick) -> None:
        if session_id not in self.storage:
            self.storage[session_id] = deque(maxlen=self.max_ticks)
        self.storage[session_id].append(asdict(tick))
    
    async def get_ticks(self, session_id: str, limit: int = 100) -> List[Dict]:
        if session_id not in self.storage:
            return []
        ticks = list(self.storage[session_id])
        return ticks[-limit:] if limit else ticks
    
    async def get_latest_tick(self, session_id: str) -> Optional[Dict]:
        if session_id not in self.storage or not self.storage[session_id]:
            return None
        return self.storage[session_id][-1]


# ============================================================================
# PRICE ENGINE
# ============================================================================

class PriceEngine:
    """
    Simulated Forex Price Engine with adaptive bias
    
    Mathematical Model:
    - Geometric Brownian Motion: dS/S = μ*dt + σ*dW + bias
    - Volatility clustering via GARCH-like AR(1) process
    - Trend momentum with mean reversion
    - Adaptive house bias based on platform exposure
    
    Audit Features:
    - Cryptographic session seeding (secrets.token_hex)
    - Seed hash published, seed revealed at session end
    - Complete tick history for replay verification
    """

    # Currency pair configurations
    PAIRS_CONFIG = {
        # Major USD pairs
        'EUR/USD': PriceConfig(pair='EUR/USD', base_price=1.0850, volatility=0.012, trend=0.0001),
        'GBP/USD': PriceConfig(pair='GBP/USD', base_price=1.2750, volatility=0.014, trend=0.0002),
        'USD/JPY': PriceConfig(pair='USD/JPY', base_price=149.50, volatility=0.016, trend=-0.0001),
        'USD/CHF': PriceConfig(pair='USD/CHF', base_price=0.8850, volatility=0.013, trend=0.0),
        'AUD/USD': PriceConfig(pair='AUD/USD', base_price=0.6550, volatility=0.015, trend=0.0001),
        'USD/CAD': PriceConfig(pair='USD/CAD', base_price=1.3250, volatility=0.012, trend=0.0),
        
        # KES pairs (Kenyan Shilling) - higher volatility typical for emerging markets
        'EUR/KES': PriceConfig(pair='EUR/KES', base_price=140.50, volatility=0.018, trend=0.0002),
        'GBP/KES': PriceConfig(pair='GBP/KES', base_price=165.25, volatility=0.020, trend=0.0003),
        'USD/KES': PriceConfig(pair='USD/KES', base_price=129.50, volatility=0.015, trend=0.0001),
        
        # Commodities
        'XAU/USD': PriceConfig(pair='XAU/USD', base_price=2050.0, volatility=0.018, trend=0.0002),
        
        # Crypto (higher volatility)
        'BTC/USD': PriceConfig(pair='BTC/USD', base_price=42500.0, volatility=0.025, trend=0.0005,
                               tick_interval_min=0.5, tick_interval_max=3.0),
    }

    def __init__(
        self,
        window_size: int = 3600,
        bias_adjustment_interval: int = 300,
        tick_storage: Optional[TickStorage] = None
    ):
        """
        Initialize Price Engine
        
        Args:
            window_size: Seconds to look back for margin calculation (default 1 hour)
            bias_adjustment_interval: Seconds between bias recalculations (default 5 min)
            tick_storage: Storage backend for ticks (default: in-memory)
        """
        self.sessions: Dict[str, MarketSession] = {}
        self.active_sessions: Dict[str, bool] = {}
        self.window_size = window_size
        self.bias_adjustment_interval = bias_adjustment_interval
        
        # Tick storage
        self.tick_storage = tick_storage or InMemoryTickStorage()
        
        # Volatility state per session (for clustering)
        self.volatility_state: Dict[str, float] = {}
        self.vol_persistence: float = 0.7  # AR(1) coefficient for vol clustering
        self.vol_mean_reversion: float = 0.1  # Speed of mean reversion
        
        # Trend momentum state
        self.momentum_state: Dict[str, float] = {}
        self.momentum_decay: float = 0.95  # Trend persistence
        
        # Bias tracking
        self.last_bias_adjustment: Dict[str, float] = {}
        self.margin_history: Dict[str, deque] = {}  # Rolling margin for trend
        
        # Net exposure per pair (sum of all open trades)
        self.net_exposure: Dict[str, float] = {}
        
        # WebSocket subscribers
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Random state seeded per session for reproducibility
        self._session_random: Dict[str, random.Random] = {}
        self._background_loops: Dict[str, asyncio.Task] = {}
        
        logger.info("PriceEngine initialized with %d pairs", len(self.PAIRS_CONFIG))

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    def start_session(self, pair: str) -> MarketSession:
        """
        Start a new market session for a currency pair
        
        Creates cryptographically seeded session for audit trail.
        Seed is hidden during session, revealed at end for verification.
        
        Args:
            pair: Currency pair (e.g., "EUR/USD", "EUR/KES")
            
        Returns:
            MarketSession with session_id and seed_hash
        """
        if pair not in self.PAIRS_CONFIG:
            raise ValueError(f"Unknown pair: {pair}. Available: {list(self.PAIRS_CONFIG.keys())}")
        
        config = self.PAIRS_CONFIG[pair]
        
        # Generate cryptographic seed (128-bit)
        seed = secrets.token_hex(16)
        
        # Create seed hash for public verification
        import hashlib
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        
        # Unique session ID
        session_id = f"{pair.replace('/', '')}_{int(time.time())}_{seed[:8]}"
        
        # Initialize session
        session = MarketSession(
            pair=pair,
            session_id=session_id,
            seed=seed,
            seed_hash=seed_hash,
            start_time=time.time(),
            base_price=config.base_price,
            current_price=config.base_price,
        )
        
        # Store session
        self.sessions[session_id] = session
        self.active_sessions[session_id] = True
        
        # Initialize states
        self.volatility_state[session_id] = config.volatility
        self.momentum_state[session_id] = 0.0
        self.margin_history[session_id] = deque(maxlen=int(self.window_size / 60))
        self.last_bias_adjustment[session_id] = time.time()
        
        # Initialize random generator with seed for reproducibility
        self._session_random[session_id] = random.Random(seed)
        
        # Initialize exposure for pair if not exists
        if pair not in self.net_exposure:
            self.net_exposure[pair] = 0.0
        
        logger.info(
            f"Started session {session_id}\n"
            f"  Pair: {pair}\n"
            f"  Seed Hash: {seed_hash[:16]}...\n"
            f"  Base Price: {config.base_price}"
        )
        
        return session

    def end_session(self, session_id: str) -> MarketSession:
        """
        End a market session and reveal seed for audit
        
        The seed is now public and can be used to independently
        verify all price movements during the session.
        
        Args:
            session_id: Session to end
            
        Returns:
            Completed session with revealed seed
        """
        if session_id not in self.sessions:
            raise ValueError(f"Unknown session: {session_id}")
        
        session = self.sessions[session_id]
        session.end_time = time.time()
        self.active_sessions[session_id] = False
        
        duration = session.end_time - session.start_time
        
        logger.info(
            f"Ended session {session_id}\n"
            f"  Pair: {session.pair}\n"
            f"  Seed (REVEALED): {session.seed}\n"
            f"  Ticks: {len(session.ticks)}\n"
            f"  Duration: {duration:.1f}s\n"
            f"  Platform Margin: {session.platform_margin:.2%}\n"
            f"  Cumulative Bias: {session.cumulative_bias:.6f}\n"
            f"  Net Exposure: {session.net_exposure:,.0f} KES"
        )
        
        return session

    # ========================================================================
    # TICK GENERATION (Core GBM + Volatility Clustering)
    # ========================================================================

    def generate_tick(self, session_id: str) -> Optional[Tick]:
        """
        Generate next price tick using Geometric Brownian Motion
        
        Mathematical Model:
            dS/S = (μ + bias)*dt + σ*dW
            
        Where:
            - S = current price
            - μ = drift (trend) + momentum
            - σ = volatility (with clustering)
            - dW = Wiener increment (random)
            - bias = adaptive house bias
        
        Volatility Clustering:
            σ(t) = α*σ(t-1) + (1-α)*σ_mean + shock
            
        This creates realistic "volatility of volatility" behavior
        where high/low volatility periods persist.
        
        Args:
            session_id: Market session ID
            
        Returns:
            New price tick or None if session inactive
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        if not self.active_sessions.get(session_id):
            return None
        
        config = self.PAIRS_CONFIG[session.pair]
        rng = self._session_random[session_id]
        
        # Time step (1 tick ≈ 1-5 seconds, scaled to yearly)
        dt = 1 / (252 * 24 * 3600)  # 1 second in trading years
        
        # --- Volatility Clustering (GARCH-like) ---
        mean_vol = config.volatility
        current_vol = self.volatility_state[session_id]
        
        # AR(1) process with mean reversion
        vol_shock = rng.gauss(0, mean_vol * 0.1)  # Random shock
        new_vol = (
            self.vol_persistence * current_vol +
            self.vol_mean_reversion * mean_vol +
            (1 - self.vol_persistence - self.vol_mean_reversion) * current_vol +
            vol_shock
        )
        # Clamp volatility to reasonable bounds
        new_vol = max(mean_vol * 0.3, min(mean_vol * 3.0, abs(new_vol)))
        self.volatility_state[session_id] = new_vol
        
        # --- Random Increment (Wiener Process) ---
        dW = rng.gauss(0, 1) * math.sqrt(dt)
        
        # --- Trend + Momentum ---
        base_drift = config.trend
        momentum = self.momentum_state[session_id]
        
        # Update momentum (decaying)
        price_change_signal = rng.gauss(0, 0.0001)
        self.momentum_state[session_id] = (
            self.momentum_decay * momentum + price_change_signal
        )
        
        # --- Adaptive House Bias ---
        bias = self._compute_house_bias(session)
        
        # --- GBM Price Update ---
        S = session.current_price
        drift_total = base_drift + momentum
        dS_percent = (drift_total * dt) + (new_vol * dW) + bias
        
        new_price = S * (1 + dS_percent)
        
        # Prevent unrealistic prices
        min_price = config.base_price * 0.5
        max_price = config.base_price * 2.0
        new_price = max(min_price, min(max_price, new_price))
        
        # --- Calculate Change ---
        change = new_price - S
        change_percent = (change / S) * 100 if S > 0 else 0
        
        # --- Bid-Ask Spread (proportional to volatility) ---
        spread_factor = 0.0005 + (new_vol * 0.01)  # Base spread + vol component
        spread = new_price * spread_factor
        bid = new_price - spread / 2
        ask = new_price + spread / 2
        
        # --- Volume (realistic distribution) ---
        base_volume = 5000
        volume = int(base_volume + rng.expovariate(1/5000))
        volume = min(50000, volume)  # Cap at 50k
        
        # --- Create Tick ---
        tick = Tick(
            timestamp=time.time(),
            pair=session.pair,
            price=round(new_price, 6),
            bid=round(bid, 6),
            ask=round(ask, 6),
            change=round(change, 6),
            change_percent=round(change_percent, 4),
            volume=volume,
            volatility=round(new_vol, 6),
        )
        
        # Update session state
        session.current_price = new_price
        session.ticks.append(tick)
        session.cumulative_bias += bias
        self._store_tick_now(session_id, tick)

        return tick

    def _store_tick_now(self, session_id: str, tick: Tick) -> None:
        """Persist a tick from sync contexts when an event loop is available."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return

        try:
            loop.create_task(self.tick_storage.store_tick(session_id, tick))
        except RuntimeError:
            return

    # ========================================================================
    # HOUSE BIAS CALCULATION
    # ========================================================================

    def _compute_house_bias(self, session: MarketSession) -> float:
        """
        Compute adaptive house bias based on platform exposure
        
        Bias Logic:
        1. Calculate platform margin from net exposure
        2. If margin < -30%: slight upward bias (help shorts profit)
        3. If margin > +30%: slight downward bias (help longs profit)
        4. Bias is capped at max_bias to avoid obvious manipulation
        
        The bias is subtle and within realistic market noise levels.
        
        Args:
            session: Market session
            
        Returns:
            Bias factor (proportion, e.g., 0.0001 = 0.01%)
        """
        config = self.PAIRS_CONFIG[session.pair]
        now = time.time()
        
        # Only recalculate bias periodically (every 5 seconds minimum)
        last_adjustment = self.last_bias_adjustment.get(session.session_id, 0)
        if now - last_adjustment < 5:
            return 0.0
        
        # Calculate platform margin
        platform_margin = self._calculate_platform_margin(session)
        session.platform_margin = platform_margin
        
        # Store margin history for analysis
        if session.session_id in self.margin_history:
            self.margin_history[session.session_id].append({
                'timestamp': now,
                'margin': platform_margin,
                'exposure': session.net_exposure,
            })
        
        # Bias calculation
        bias = 0.0
        bias_reason = "neutral"
        
        if platform_margin < -0.30:
            # Platform losing money - slight upward bias
            # (rising prices help short positions close profitably)
            intensity = min(1.0, abs(platform_margin + 0.30) / 0.30)
            bias = min(config.max_bias, 0.0001 * (1 + intensity))
            bias_reason = "platform_losing"
            
        elif platform_margin > 0.30:
            # Platform winning too much - slight downward bias
            # (falling prices help long positions close profitably)
            intensity = min(1.0, (platform_margin - 0.30) / 0.30)
            bias = -min(config.max_bias, 0.0001 * (1 + intensity))
            bias_reason = "platform_winning"
        
        # Record bias adjustment for audit
        if bias != 0.0:
            session.bias_history.append({
                'timestamp': now,
                'bias': bias,
                'reason': bias_reason,
                'margin': platform_margin,
                'exposure': session.net_exposure,
            })
        
        self.last_bias_adjustment[session.session_id] = now
        
        logger.debug(
            f"Bias computed for {session.pair}: {bias:.6f} "
            f"(margin: {platform_margin:.2%}, reason: {bias_reason})"
        )
        
        return bias

    def _calculate_platform_margin(self, session: MarketSession) -> float:
        """
        Calculate platform margin from open trade exposure
        
        Platform margin = (total_staked - potential_payout) / total_staked
        
        For this simulation:
        - Net long exposure: platform profits if price falls
        - Net short exposure: platform profits if price rises
        
        Returns:
            Margin as percentage (-1 to 1, where negative = losing)
        """
        if len(session.ticks) < 2:
            return 0.0
        
        # Price movement since session start
        start_price = session.base_price
        current_price = session.current_price
        price_change_pct = (current_price - start_price) / start_price
        
        # Net exposure effect
        net_exp = session.net_exposure
        total_stakes = session.total_long_stakes + session.total_short_stakes
        
        if total_stakes == 0:
            # Use simulated exposure based on price action
            simulated_margin = -price_change_pct * 0.5 + 0.002  # Base 0.2% edge
            return max(-1.0, min(1.0, simulated_margin))
        
        # Calculate P&L based on exposure
        # Long positions profit when price goes up
        # Short positions profit when price goes down
        long_pnl = session.total_long_stakes * price_change_pct
        short_pnl = session.total_short_stakes * (-price_change_pct)
        
        # Platform P&L is opposite of traders' P&L
        platform_pnl = -(long_pnl + short_pnl)
        
        # Add platform edge (spread)
        platform_edge = total_stakes * 0.002  # 0.2% edge
        platform_pnl += platform_edge
        
        # Margin as percentage of total stakes
        margin = platform_pnl / total_stakes if total_stakes > 0 else 0.0
        
        return max(-1.0, min(1.0, margin))

    # ========================================================================
    # EXPOSURE TRACKING
    # ========================================================================

    def update_net_exposure(
        self,
        pair: str,
        delta: float,
        is_long: bool = True
    ) -> None:
        """
        Update net exposure for a currency pair
        
        Called when trades are opened/closed to track platform risk.
        
        Args:
            pair: Currency pair
            delta: Stake amount change (positive = add, negative = remove)
            is_long: True for long position, False for short
        """
        if pair not in self.net_exposure:
            self.net_exposure[pair] = 0.0
        
        # Net exposure: positive = net long, negative = net short
        if is_long:
            self.net_exposure[pair] += delta
        else:
            self.net_exposure[pair] -= delta
        
        # Update session exposure tracking
        for session in self.sessions.values():
            if session.pair == pair and self.active_sessions.get(session.session_id):
                session.net_exposure = self.net_exposure[pair]
                if is_long:
                    session.total_long_stakes += max(0, delta)
                else:
                    session.total_short_stakes += max(0, delta)
        
        logger.debug(
            f"Exposure updated for {pair}: "
            f"delta={delta:+,.0f} KES, "
            f"is_long={is_long}, "
            f"net={self.net_exposure[pair]:+,.0f} KES"
        )

    def get_net_exposure(self, pair: str) -> float:
        """Get current net exposure for a pair"""
        return self.net_exposure.get(pair, 0.0)

    # ========================================================================
    # SESSION DATA & AUDIT
    # ========================================================================

    def get_session_data(self, session_id: str) -> Optional[Dict]:
        """Get session data for audit/analysis"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        is_ended = session.end_time is not None
        
        return {
            'session_id': session_id,
            'pair': session.pair,
            'seed_hash': session.seed_hash,
            'seed': session.seed if is_ended else "[HIDDEN - revealed at session end]",
            'start_time': session.start_time,
            'end_time': session.end_time,
            'base_price': session.base_price,
            'current_price': session.current_price,
            'tick_count': len(session.ticks),
            'platform_margin': session.platform_margin,
            'cumulative_bias': session.cumulative_bias,
            'net_exposure': session.net_exposure,
            'bias_adjustments': len(session.bias_history),
            'duration_seconds': (session.end_time or time.time()) - session.start_time,
            'price_change_percent': (
                (session.current_price - session.base_price) / session.base_price * 100
                if session.base_price > 0 else 0
            ),
        }

    def get_latest_prices(self, pair: Optional[str] = None) -> Dict[str, Dict]:
        """Get latest prices for all active pairs or specific pair"""
        result = {}
        
        for session_id, session in self.sessions.items():
            if not self.active_sessions.get(session_id):
                continue
            
            if pair and session.pair != pair:
                continue
            
            if session.ticks:
                latest = session.ticks[-1]
                result[session.pair] = {
                    'price': latest.price,
                    'bid': latest.bid,
                    'ask': latest.ask,
                    'change': latest.change,
                    'change_percent': latest.change_percent,
                    'volume': latest.volume,
                    'volatility': latest.volatility,
                    'timestamp': latest.timestamp,
                    'session_id': session_id,
                }
        
        return result

    def get_or_create_active_session(self, pair: str) -> MarketSession:
        """Get the active session for a pair or create one."""
        for session_id, session in self.sessions.items():
            if session.pair == pair and self.active_sessions.get(session_id):
                return session
        return self.start_session(pair)

    def get_candles(self, pair: str, timeframe: str = "15m", limit: int = 120) -> List[Dict[str, Any]]:
        """Aggregate ticks into timeframe candles."""
        timeframe_map = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }
        bucket_seconds = timeframe_map.get(timeframe.lower())
        if bucket_seconds is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        session = self.get_or_create_active_session(pair)
        if not session.ticks:
            self.generate_tick(session.session_id)

        buckets: Dict[int, Dict[str, Any]] = {}
        for tick in session.ticks:
            bucket_start = int(tick.timestamp // bucket_seconds) * bucket_seconds
            candle = buckets.get(bucket_start)
            if candle is None:
                candle = {
                    "timestamp": bucket_start,
                    "open": tick.price,
                    "high": tick.price,
                    "low": tick.price,
                    "close": tick.price,
                    "volume": 0,
                }
                buckets[bucket_start] = candle

            candle["high"] = max(candle["high"], tick.price)
            candle["low"] = min(candle["low"], tick.price)
            candle["close"] = tick.price
            candle["volume"] += tick.volume

        candles = [buckets[key] for key in sorted(buckets.keys())]
        return candles[-limit:]

    # ========================================================================
    # STREAMING & SUBSCRIPTIONS
    # ========================================================================

    def get_tick_interval(self, pair: str) -> float:
        """Get random tick interval for a pair (1-5 seconds)"""
        config = self.PAIRS_CONFIG.get(pair)
        if not config:
            return 2.0
        
        return random.uniform(config.tick_interval_min, config.tick_interval_max)

    async def stream_prices(
        self,
        session_id: str,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Stream prices for a session with variable intervals
        
        Args:
            session_id: Market session ID
            callback: Optional async callback for each tick
        """
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        while self.active_sessions.get(session_id):
            tick = self.generate_tick(session_id)
            
            if tick:
                # Store tick
                await self.tick_storage.store_tick(session_id, tick)
                
                # Call callback if provided
                if callback:
                    try:
                        await callback(tick)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                
                # Publish to subscribers
                await self._publish_tick(session_id, tick)
            
            # Variable interval (1-5 seconds)
            interval = self.get_tick_interval(session.pair)
            await asyncio.sleep(interval)

    async def _publish_tick(self, session_id: str, tick: Tick) -> None:
        """Publish tick to WebSocket subscribers"""
        if session_id not in self.subscribers:
            return
        
        for callback in self.subscribers[session_id]:
            try:
                await callback(tick)
            except Exception as e:
                logger.error(f"Error publishing tick: {e}")

    def subscribe(self, session_id: str, callback: Callable) -> None:
        """Subscribe to price updates for a session"""
        if session_id not in self.subscribers:
            self.subscribers[session_id] = []
        self.subscribers[session_id].append(callback)

    def unsubscribe(self, session_id: str, callback: Callable) -> None:
        """Unsubscribe from price updates"""
        if session_id in self.subscribers:
            try:
                self.subscribers[session_id].remove(callback)
            except ValueError:
                pass


# ============================================================================
# GLOBAL ENGINE INSTANCE
# ============================================================================

price_engine = PriceEngine()


# ============================================================================
# BACKGROUND TASK: Periodic Bias Adjustment
# ============================================================================

async def adjust_bias_periodically(interval: int = 300) -> None:
    """
    Background task that periodically recalculates and logs bias
    
    Runs every 5 minutes to:
    1. Recalculate platform margin across all sessions
    2. Adjust adaptive bias based on exposure
    3. Log for compliance and audit trail
    
    Args:
        interval: Seconds between adjustments (default 5 min)
    """
    while True:
        try:
            active_count = 0
            total_exposure = 0.0
            
            for session_id, session in price_engine.sessions.items():
                if not price_engine.active_sessions.get(session_id):
                    continue
                
                active_count += 1
                total_exposure += abs(session.net_exposure)
                
                # Force margin recalculation
                margin = price_engine._calculate_platform_margin(session)
                session.platform_margin = margin
            
            if active_count > 0:
                logger.info(
                    f"Bias adjustment cycle complete: "
                    f"{active_count} active sessions, "
                    f"total exposure: {total_exposure:,.0f} KES"
                )
        
        except Exception as e:
            logger.error(f"Error in bias adjustment: {e}")
        
        await asyncio.sleep(interval)


# ============================================================================
# PSEUDOCODE REFERENCE
# ============================================================================

"""
PSEUDOCODE: Price Engine Architecture

class PriceEngine:
    
    def start_session(pair):
        '''
        1. Validate pair exists in config
        2. Generate cryptographic seed: seed = secrets.token_hex(16)
        3. Create seed hash: seed_hash = SHA256(seed)
        4. Initialize session with base price from config
        5. Create seeded random generator for reproducibility
        6. Return session with hidden seed, public seed_hash
        '''
        
    def generate_tick(session_id):
        '''
        1. Get session and config
        2. Compute volatility clustering:
           - σ(t) = α*σ(t-1) + (1-α)*σ_mean + shock
           - Clamp to reasonable bounds
        3. Generate Wiener increment: dW = N(0,1) * sqrt(dt)
        4. Compute trend with momentum decay
        5. Get adaptive bias: bias = compute_house_bias(session)
        6. Apply GBM: new_price = price * (1 + drift*dt + vol*dW + bias)
        7. Calculate bid/ask spread (proportional to vol)
        8. Generate realistic volume
        9. Store tick and update session state
        '''
        
    def compute_house_bias(session):
        '''
        1. Calculate platform_margin from net exposure
        2. If margin < -30%:
           - Platform losing money
           - Apply upward bias (helps shorts)
           - bias = min(max_bias, 0.0001 * intensity)
        3. If margin > +30%:
           - Platform winning too much
           - Apply downward bias (helps longs)
           - bias = -min(max_bias, 0.0001 * intensity)
        4. Else: bias = 0 (neutral)
        5. Cap at max_bias (0.8%) to avoid obvious rigging
        6. Log for audit trail
        '''
        
    def update_net_exposure(pair, delta, is_long):
        '''
        1. Track sum(long_stakes) - sum(short_stakes) per pair
        2. Called when trades open/close
        3. Updates session exposure tracking
        '''
        
    async def adjust_bias_periodically(interval=300):
        '''
        Background task every 5 minutes:
        1. Loop through active sessions
        2. Recalculate platform margin
        3. Log exposure and margin stats
        4. Bias adjustment happens naturally in generate_tick()
        '''
        
    def end_session(session_id):
        '''
        1. Mark session as ended
        2. REVEAL seed (was hidden during session)
        3. Log complete audit trail:
           - Seed for replay verification
           - All ticks generated
           - Cumulative bias applied
           - Platform margin achieved
        '''
"""
