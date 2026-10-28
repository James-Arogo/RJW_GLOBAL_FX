"""Trade schemas."""

from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models import TradeDirection, TradeStatus


class TradeCreate(BaseModel):
    """Schema for creating a trade."""
    
    pair: str = Field(..., example="EUR/USD")
    direction: TradeDirection
    stake_kes: float = Field(..., ge=50, description="Minimum KSh 50")
    leverage: float = Field(5.0, ge=1, le=50, description="Position leverage multiplier")
    open_price: Optional[float] = Field(None, gt=0, description="Auto-generated if not provided")
    stop_loss_kes: Optional[float] = Field(None, ge=0)
    take_profit_kes: Optional[float] = Field(None, ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pair": "EUR/USD",
                "direction": "long",
                "stake_kes": 5000.0,
                "leverage": 10.0,
                "open_price": 1.0850,
                "stop_loss_kes": 500.0,
                "take_profit_kes": 1000.0
            }
        }


class TradeResponse(BaseModel):
    """Schema for trade response."""
    
    id: UUID
    user_id: UUID
    pair: str
    direction: TradeDirection
    stake_kes: float
    leverage: float = 1.0
    margin_required_kes: Optional[float] = None
    notional_value_kes: Optional[float] = None
    quantity_units: Optional[float] = None
    liquidation_price: Optional[float] = None
    open_price: float
    current_price: Optional[float] = None
    close_price: Optional[float] = None
    stop_loss_kes: Optional[float] = None
    take_profit_kes: Optional[float] = None
    status: TradeStatus
    profit_kes: Optional[float] = None
    profit_percent: Optional[float] = None
    unrealized_pnl_kes: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    created_at: datetime
    close_time: Optional[datetime] = None
    disclaimer: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "223e4567-e89b-12d3-a456-426614174001",
                "pair": "EUR/USD",
                "trade_type": "BUY",
                "amount": 5000.0,
                "entry_price": 1.0850,
                "exit_price": 1.0900,
                "stop_loss": 500.0,
                "take_profit": 1000.0,
                "status": "CLOSED",
                "pnl": 385.0,
                "pnl_percent": 7.7,
                "created_at": "2024-01-29T12:00:00",
                "closed_at": "2024-01-29T13:00:00",
                "disclaimer": "This is a simulated forex game..."
            }
        }


class PositionSummary(BaseModel):
    """Open position with live mark-to-market details."""

    id: UUID
    pair: str
    direction: TradeDirection
    status: TradeStatus
    stake_kes: float
    leverage: float
    margin_required_kes: float
    notional_value_kes: float
    quantity_units: float
    open_price: float
    current_price: float
    liquidation_price: float
    unrealized_pnl_kes: float
    unrealized_pnl_percent: float
    stop_loss_kes: Optional[float] = None
    take_profit_kes: Optional[float] = None
    open_time: datetime


class OpenPositionsResponse(BaseModel):
    """Grouped open position payload."""

    open_positions: int
    used_margin_kes: float
    total_notional_kes: float
    unrealized_pnl_kes: float
    positions: list[PositionSummary]
    disclaimer: Optional[str] = None
