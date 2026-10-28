"""
SQLAlchemy 2.x Async Models for RJW GLOBAL FX
PostgreSQL database models for simulated forex trading platform
All currency in KES (Kenyan Shilling)
"""

from datetime import datetime, timedelta
from sqlalchemy import (
    Column, String, Float, DateTime, Boolean, Integer, Enum as SQLEnum,
    ForeignKey, JSON, Text, Index, Numeric
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from app.core.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class TradeDirection(str, Enum):
    """Trade direction: long or short"""
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, Enum):
    """Trade status"""
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class AuditEventType(str, Enum):
    """Audit log event types"""
    USER_REGISTERED = "user_registered"
    USER_VERIFIED = "user_verified"
    TRADE_OPENED = "trade_opened"
    TRADE_CLOSED = "trade_closed"
    TRADE_CANCELLED = "trade_cancelled"
    BALANCE_UPDATED = "balance_updated"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    SEED_REVEALED = "seed_revealed"
    BIAS_ADJUSTED = "bias_adjusted"


class DepositMethod(str, Enum):
    """Supported wallet funding methods."""
    MPESA = "mpesa"
    BANK = "bank"
    CARD = "card"
    SACCO = "sacco"


class DepositStatus(str, Enum):
    """Deposit processing status."""
    PENDING = "pending"
    ACTION_REQUIRED = "action_required"
    COMPLETED = "completed"
    FAILED = "failed"


class WalletTransactionType(str, Enum):
    """Wallet transaction type."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


# ============================================================================
# USER MODEL
# ============================================================================

class User(Base):
    """
    User account model
    
    Fields:
    - balance_kes: Virtual account balance in Kenyan Shillings (default 10,000)
    - is_verified: Email verification status
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Balance in KES (Kenyan Shillings)
    balance_kes = Column(Numeric(15, 2), default=10000.00, nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    deposits = relationship("DepositTransaction", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} ({self.balance_kes} KES)>"


# ============================================================================
# TRADE MODEL
# ============================================================================

class Trade(Base):
    """
    Trade record model
    
    Tracks individual user trades with complete lifecycle:
    - Open: entry price, time, direction
    - Close: exit price, time, payout, profit
    
    All amounts in KES (Kenyan Shillings)
    """
    __tablename__ = "trades"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Trade Details
    pair = Column(String(20), nullable=False)  # e.g., "EUR/USD", "GBP/USD"
    direction = Column(SQLEnum(TradeDirection), nullable=False)  # "long" or "short"
    stake_kes = Column(Numeric(12, 2), nullable=False)  # Min 50 KES
    
    # Entry (Open Trade)
    open_price = Column(Numeric(15, 6), nullable=False)
    open_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Exit (Close Trade)
    close_price = Column(Numeric(15, 6), nullable=True)
    close_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Trade duration in seconds
    
    # Status
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.OPEN, nullable=False, index=True)
    
    # Outcomes (in KES)
    payout_kes = Column(Numeric(12, 2), nullable=True)  # Total payout (stake + profit)
    profit_kes = Column(Numeric(12, 2), nullable=True)  # Pure profit/loss
    profit_percent = Column(Numeric(6, 2), nullable=True)  # ROI percentage
    
    # Trade Metadata
    stop_loss_kes = Column(Numeric(12, 2), nullable=True)  # Stop loss in KES
    take_profit_kes = Column(Numeric(12, 2), nullable=True)  # Take profit in KES
    
    # Risk Metrics
    risk_reward_ratio = Column(Numeric(6, 2), nullable=True)  # TP:SL ratio
    leverage = Column(Numeric(6, 2), default=1.0, nullable=False)
    margin_required_kes = Column(Numeric(12, 2), nullable=True)
    notional_value_kes = Column(Numeric(12, 2), nullable=True)
    quantity_units = Column(Numeric(18, 8), nullable=True)
    liquidation_price = Column(Numeric(15, 6), nullable=True)
    
    # Session Reference (for audit trail)
    market_session_id = Column(UUID(as_uuid=True), ForeignKey("market_sessions.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    market_session = relationship("MarketSession", back_populates="trades")
    
    def __repr__(self):
        status_icon = "📈" if self.direction == TradeDirection.LONG else "📉"
        return f"<Trade {status_icon}{self.pair} {self.stake_kes}KES {self.status}>"


# ============================================================================
# MARKET SESSION MODEL
# ============================================================================

class MarketSession(Base):
    """
    Market session for price generation tracking
    
    Each session:
    - Generates prices for a currency pair
    - Uses cryptographic seed for audit trail
    - Tracks platform bias and margin
    - Reveals seed after session for verification
    """
    __tablename__ = "market_sessions"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pair = Column(String(20), nullable=False, index=True)  # e.g., "EUR/USD"
    
    # Session Timing
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    
    # Cryptographic Audit Trail
    seed_hash = Column(String(64), nullable=False)  # SHA-256 hash of seed (hidden)
    seed_reveal = Column(String(64), nullable=True)  # Actual seed (revealed after session ends)
    
    # Session Parameters (JSON)
    engine_params = Column(JSON, nullable=True)  # {volatility, drift, base_price, max_bias}
    
    # Trading Statistics During Session
    base_price = Column(Numeric(15, 6), nullable=False)
    final_price = Column(Numeric(15, 6), nullable=True)
    price_change_percent = Column(Numeric(6, 2), nullable=True)
    
    # Platform Metrics During Session
    platform_margin_kes = Column(Numeric(12, 2), default=0.0, nullable=False)
    cumulative_bias = Column(Numeric(10, 6), default=0.0, nullable=False)
    net_exposure_kes = Column(Numeric(12, 2), default=0.0, nullable=False)
    
    # Tick Data
    tick_count = Column(Integer, default=0, nullable=False)
    avg_volatility = Column(Numeric(6, 4), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="market_session")
    
    def __repr__(self):
        return f"<MarketSession {self.pair} {self.start_time.strftime('%Y-%m-%d %H:%M')}>"


# ============================================================================
# PLATFORM METRIC MODEL
# ============================================================================

class PlatformMetric(Base):
    """
    Daily platform-wide metrics for analytics and compliance
    
    Tracks:
    - Daily and total trading volume
    - Platform profitability
    - Risk metrics
    """
    __tablename__ = "platform_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_date = Column(DateTime, nullable=False, index=True)  # Date of metric
    
    # Volume Metrics (in KES)
    daily_staked_kes = Column(Numeric(15, 2), default=0.0, nullable=False)
    total_staked_kes = Column(Numeric(18, 2), default=0.0, nullable=False)  # Cumulative
    
    # Payout Metrics (in KES)
    daily_payout_kes = Column(Numeric(15, 2), default=0.0, nullable=False)
    total_payout_kes = Column(Numeric(18, 2), default=0.0, nullable=False)  # Cumulative
    
    # Platform Profit (in KES)
    daily_platform_profit_kes = Column(Numeric(15, 2), default=0.0, nullable=False)
    total_platform_profit_kes = Column(Numeric(18, 2), default=0.0, nullable=False)
    
    # Trading Statistics
    total_trades_opened = Column(Integer, default=0, nullable=False)
    total_trades_closed = Column(Integer, default=0, nullable=False)
    avg_trade_duration_seconds = Column(Integer, nullable=True)
    
    # Win/Loss Metrics
    total_winning_trades = Column(Integer, default=0, nullable=False)
    total_losing_trades = Column(Integer, default=0, nullable=False)
    platform_win_rate_percent = Column(Numeric(5, 2), nullable=True)
    
    # Risk Metrics
    max_concurrent_exposure_kes = Column(Numeric(15, 2), nullable=True)
    avg_concurrent_exposure_kes = Column(Numeric(15, 2), nullable=True)
    
    # User Statistics
    active_users = Column(Integer, default=0, nullable=False)
    new_users = Column(Integer, default=0, nullable=False)
    verified_users = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlatformMetric {self.metric_date.strftime('%Y-%m-%d')} ({self.daily_platform_profit_kes}KES)>"


# ============================================================================
# DEPOSIT TRANSACTION MODEL
# ============================================================================

class DepositTransaction(Base):
    """
    Wallet funding transaction for simulated deposits.

    This stores deposit requests and credits the user's simulated balance.
    """
    __tablename__ = "deposit_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    method = Column(SQLEnum(DepositMethod), nullable=False, index=True)
    transaction_type = Column(SQLEnum(WalletTransactionType), default=WalletTransactionType.DEPOSIT, nullable=False, index=True)
    status = Column(SQLEnum(DepositStatus), default=DepositStatus.PENDING, nullable=False, index=True)
    amount_kes = Column(Numeric(15, 2), nullable=False)

    reference = Column(String(100), unique=True, nullable=False, index=True)
    provider = Column(String(120), nullable=True)
    phone_number = Column(String(30), nullable=True)
    institution_name = Column(String(120), nullable=True)
    account_reference = Column(String(120), nullable=True)
    provider_reference = Column(String(120), nullable=True)
    checkout_url = Column(String(255), nullable=True)
    provider_status = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="deposits")

    def __repr__(self):
        return f"<DepositTransaction {self.reference} {self.amount_kes}KES {self.status.value}>"


# ============================================================================
# AUDIT LOG MODEL
# ============================================================================

class AuditLog(Base):
    """
    Audit log for compliance and transparency
    
    Tracks all significant events:
    - User actions (register, verify, login)
    - Trade lifecycle (open, close, cancel)
    - Platform events (sessions, bias adjustments)
    - Balance changes
    
    Immutable record for regulatory compliance
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Event Information
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    event_description = Column(String(500), nullable=False)
    
    # Related Resources
    trade_id = Column(UUID(as_uuid=True), ForeignKey("trades.id"), nullable=True)
    market_session_id = Column(UUID(as_uuid=True), ForeignKey("market_sessions.id"), nullable=True)
    
    # Event Data (JSON)
    event_data = Column(JSON, nullable=True)  # Additional context as JSON
    
    # Change Tracking
    previous_value = Column(Text, nullable=True)  # Previous value (if applicable)
    new_value = Column(Text, nullable=True)  # New value (if applicable)
    
    # IP/User Agent
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.event_type.value} {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}>"


# ============================================================================
# MODEL INDEXES FOR PERFORMANCE
# ============================================================================

# Additional composite indexes for common queries
"""
Indexes created:

USER INDEXES:
- ix_users_username (unique)
- ix_users_email (unique)
- users.created_at

TRADE INDEXES:
- ix_trades_user_id
- ix_trades_pair
- ix_trades_user_pair (composite: user_id + pair)
- ix_trades_status
- ix_trades_created_at

MARKET SESSION INDEXES:
- ix_market_sessions_pair
- ix_market_sessions_start_time

PLATFORM METRIC INDEXES:
- ix_platform_metrics_date

AUDIT LOG INDEXES:
- ix_audit_logs_user_id
- ix_audit_logs_event_type
- ix_audit_logs_created_at
"""


# ============================================================================
# RELATIONSHIPS SUMMARY
# ============================================================================

"""
Relationship Diagram:

User (1) ──┬──────> Trade (Many)
           │
           └──────> AuditLog (Many)

MarketSession (1) ──> Trade (Many)
MarketSession (1) ──> AuditLog (Many)

Trade ──> MarketSession (optional)

Constraints:
- DELETE User CASCADE deletes: Trades, AuditLogs
- DELETE MarketSession: Trades set market_session_id = NULL
- DELETE Trade: AuditLogs remain (audit trail is immutable)
"""
