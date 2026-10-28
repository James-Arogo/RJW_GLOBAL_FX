"""Portfolio model for tracking user statistics."""

from datetime import datetime
from sqlalchemy import Column, Float, DateTime, ForeignKey, Integer, String
import uuid
from app.core.database import Base


class Portfolio(Base):
    """Portfolio model for user trading statistics and analytics."""
    
    __tablename__ = "portfolios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Trade statistics
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    total_pnl = Column(Float, default=0.0, nullable=False)  # Total profit/loss
    win_rate = Column(Float, default=0.0, nullable=False)  # Percentage
    average_win = Column(Float, default=0.0, nullable=False)
    average_loss = Column(Float, default=0.0, nullable=False)
    max_win = Column(Float, default=0.0, nullable=False)
    max_loss = Column(Float, default=0.0, nullable=False)
    
    # Daily/Monthly
    daily_pnl = Column(Float, default=0.0, nullable=False)
    monthly_pnl = Column(Float, default=0.0, nullable=False)
    
    # Level/Badges
    level = Column(Integer, default=1, nullable=False)
    badge = Column(String(50), default="Beginner", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Portfolio user_id={self.user_id}>"
