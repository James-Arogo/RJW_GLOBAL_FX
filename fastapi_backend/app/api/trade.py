"""Trade endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.models import TradeStatus
from app.schemas.trade import OpenPositionsResponse, TradeCreate, TradeResponse
from app.schemas.common import MessageResponse
from app.services.trade_service import TradeService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("/", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade_data: TradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new trade."""
    
    # Validate minimum stake
    if trade_data.stake_kes < settings.MIN_STAKE_KES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum stake is KSh {settings.MIN_STAKE_KES}"
        )
    
    # Check user has sufficient balance
    if trade_data.leverage > settings.MAX_LEVERAGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum leverage is {settings.MAX_LEVERAGE}x"
        )

    if float(current_user.balance_kes) < trade_data.stake_kes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance"
        )
    
    # Create trade
    trade = await TradeService.create_trade(db, str(current_user.id), trade_data)
    
    # Deduct amount from balance
    current_user.balance_kes = float(current_user.balance_kes) - trade_data.stake_kes
    await db.commit()
    
    response = TradeService.serialize_trade(trade, include_live_metrics=True)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    
    return response


@router.get("/", response_model=list[TradeResponse])
async def get_user_trades(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's trades."""
    trades = await TradeService.get_user_trades(db, str(current_user.id), limit)
    
    response = [TradeService.serialize_trade(trade, include_live_metrics=trade.status == TradeStatus.OPEN) for trade in trades]
    for item in response:
        item.disclaimer = settings.SIMULATION_DISCLAIMER
    
    return response


@router.get("/open", response_model=list[TradeResponse])
async def get_open_trades(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's open trades."""
    trades = await TradeService.get_open_trades(db, str(current_user.id))
    
    response = [TradeService.serialize_trade(trade, include_live_metrics=True) for trade in trades]
    for item in response:
        item.disclaimer = settings.SIMULATION_DISCLAIMER

    return response


@router.get("/open/positions", response_model=OpenPositionsResponse)
async def get_open_positions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get live mark-to-market open positions."""
    response = await TradeService.get_open_positions_snapshot(db, str(current_user.id))
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    return response


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific trade."""
    trade = await TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")
    
    if str(trade.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    response = TradeService.serialize_trade(trade, include_live_metrics=trade.status == TradeStatus.OPEN)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    
    return response


@router.post("/{trade_id}/close", response_model=TradeResponse)
async def close_trade(
    trade_id: str,
    exit_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Close a trade."""
    trade = await TradeService.get_trade_by_id(db, trade_id)
    
    if not trade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")
    
    if str(trade.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Close trade
    closed_trade = await TradeService.close_trade(db, trade_id, exit_price)
    
    # Update user balance (add back stake + profit)
    payout = float(closed_trade.payout_kes or 0)
    current_user.balance_kes = float(current_user.balance_kes) + payout
    await db.commit()
    
    response = TradeService.serialize_trade(closed_trade, include_live_metrics=False)
    response.disclaimer = settings.SIMULATION_DISCLAIMER
    
    return response
