"""Portfolio schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PortfolioResponse(BaseModel):
    """Schema for portfolio response."""
    
    id: str
    user_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    win_rate: float
    average_win: float
    average_loss: float
    max_win: float
    max_loss: float
    daily_pnl: float
    monthly_pnl: float
    level: int
    badge: str
    created_at: datetime
    updated_at: datetime
    disclaimer: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "223e4567-e89b-12d3-a456-426614174001",
                "total_trades": 25,
                "winning_trades": 15,
                "losing_trades": 10,
                "total_pnl": 5500.0,
                "win_rate": 60.0,
                "average_win": 400.0,
                "average_loss": 200.0,
                "max_win": 2000.0,
                "max_loss": 1000.0,
                "daily_pnl": 500.0,
                "monthly_pnl": 3000.0,
                "level": 5,
                "badge": "Silver Trader",
                "created_at": "2024-01-29T12:00:00",
                "updated_at": "2024-01-29T13:00:00",
                "disclaimer": "This is a simulated forex game..."
            }
        }
