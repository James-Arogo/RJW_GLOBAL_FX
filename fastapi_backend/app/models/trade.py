"""Trade model."""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
import uuid
from enum import Enum
from app.core.database import Base


class TradeType(str, Enum):
    """Trade type enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    """Trade status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class Trade(Base):
    """Trade model for tracking user trades."""
    
    __tablename__ = "trades"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Trade details
    pair = Column(String(20), nullable=False)  # e.g., EUR/USD
    trade_type = Column(SQLEnum(TradeType), nullable=False)
    amount = Column(Float, nullable=False)  # In KES
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=None)  # Null if still open
    
    # Risk management
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    
    # Status & P&L
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.OPEN, nullable=False)
    pnl = Column(Float, default=0.0, nullable=False)  # Profit/Loss in KES
    pnl_percent = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    closed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Trade {self.pair} {self.trade_type}>"
