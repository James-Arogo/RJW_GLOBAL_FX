"""Trade service for trade management."""

import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.config import settings
from app.models import Trade, TradeStatus, TradeDirection
from app.schemas.trade import OpenPositionsResponse, PositionSummary, TradeCreate, TradeResponse
from app.services.price_engine import price_engine
from app.services.risk_service import RiskEngine


class TradeService:
    """Service for trade operations."""

    @staticmethod
    def _normalize_uuid(value):
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                return value
        return value
    
    @staticmethod
    def get_live_price(pair: str) -> float:
        """Get the latest simulated market price for a pair."""
        session = price_engine.get_or_create_active_session(pair)
        tick = price_engine.generate_tick(session.session_id)
        return float(tick.price if tick else session.current_price)

    @staticmethod
    def build_position_snapshot(trade: Trade, current_price: float | None = None) -> dict:
        """Build live metrics for a trade."""
        margin_required_kes = float(trade.margin_required_kes or trade.stake_kes or 0)
        leverage = float(trade.leverage or 1.0)
        metrics = RiskEngine.calculate_position(
            open_price=float(trade.open_price),
            margin_kes=margin_required_kes,
            leverage=leverage,
            direction=trade.direction.value if hasattr(trade.direction, "value") else str(trade.direction),
            maintenance_margin_ratio=settings.MAINTENANCE_MARGIN_RATIO,
            current_price=current_price,
        )
        return {
            "leverage": metrics.leverage,
            "margin_required_kes": metrics.margin_required_kes,
            "notional_value_kes": metrics.notional_value_kes,
            "quantity_units": metrics.quantity_units,
            "liquidation_price": metrics.liquidation_price,
            "current_price": metrics.current_price,
            "unrealized_pnl_kes": metrics.unrealized_pnl_kes,
            "unrealized_pnl_percent": metrics.unrealized_pnl_percent,
        }

    @staticmethod
    def serialize_trade(trade: Trade, include_live_metrics: bool = False) -> TradeResponse:
        """Serialize a trade model into the API schema."""
        response = TradeResponse.model_validate(trade)
        response.leverage = float(trade.leverage or 1.0)
        response.margin_required_kes = float(trade.margin_required_kes or trade.stake_kes or 0)
        response.notional_value_kes = float(trade.notional_value_kes or response.margin_required_kes)
        response.quantity_units = float(trade.quantity_units or 0)
        response.liquidation_price = float(trade.liquidation_price or 0) if trade.liquidation_price is not None else None

        if include_live_metrics and trade.status == TradeStatus.OPEN:
            snapshot = TradeService.build_position_snapshot(trade, TradeService.get_live_price(trade.pair))
            response.current_price = snapshot["current_price"]
            response.unrealized_pnl_kes = snapshot["unrealized_pnl_kes"]
            response.unrealized_pnl_percent = snapshot["unrealized_pnl_percent"]

        return response
    
    @staticmethod
    async def create_trade(db: AsyncSession, user_id: str, trade_data: TradeCreate) -> Trade:
        """Create a new trade."""
        entry_price = trade_data.open_price or TradeService.get_live_price(trade_data.pair)
        normalized_user_id = TradeService._normalize_uuid(user_id)
        leverage = max(1.0, min(float(trade_data.leverage or settings.DEFAULT_LEVERAGE), settings.MAX_LEVERAGE))
        metrics = RiskEngine.calculate_position(
            open_price=entry_price,
            margin_kes=float(trade_data.stake_kes),
            leverage=leverage,
            direction=trade_data.direction.value,
            maintenance_margin_ratio=settings.MAINTENANCE_MARGIN_RATIO,
        )
        
        db_trade = Trade(
            user_id=normalized_user_id,
            pair=trade_data.pair,
            direction=trade_data.direction,
            stake_kes=trade_data.stake_kes,
            leverage=metrics.leverage,
            margin_required_kes=metrics.margin_required_kes,
            notional_value_kes=metrics.notional_value_kes,
            quantity_units=metrics.quantity_units,
            liquidation_price=metrics.liquidation_price,
            open_price=entry_price,
            stop_loss_kes=trade_data.stop_loss_kes,
            take_profit_kes=trade_data.take_profit_kes,
            status=TradeStatus.OPEN,
            risk_reward_ratio=(
                round(float(trade_data.take_profit_kes) / float(trade_data.stop_loss_kes), 2)
                if trade_data.stop_loss_kes and trade_data.take_profit_kes
                else None
            ),
        )
        
        db.add(db_trade)
        await db.commit()
        await db.refresh(db_trade)
        price_engine.update_net_exposure(
            trade_data.pair,
            float(metrics.notional_value_kes),
            trade_data.direction == TradeDirection.LONG,
        )
        return db_trade
    
    @staticmethod
    async def close_trade(db: AsyncSession, trade_id: str, exit_price: float | None = None) -> Trade:
        """Close a trade and calculate P&L."""
        normalized_trade_id = TradeService._normalize_uuid(trade_id)
        result = await db.execute(select(Trade).where(Trade.id == normalized_trade_id))
        trade = result.scalar_one_or_none()
        
        if not trade:
            return None
        
        resolved_exit_price = exit_price or TradeService.get_live_price(trade.pair)
        trade.close_price = resolved_exit_price
        trade.status = TradeStatus.CLOSED
        trade.close_time = datetime.utcnow()
        trade.duration_seconds = int((trade.close_time - trade.open_time).total_seconds())
        
        metrics = TradeService.build_position_snapshot(trade, resolved_exit_price)
        pnl = metrics["unrealized_pnl_kes"]
        
        trade.profit_kes = pnl
        trade.profit_percent = (pnl / float(trade.margin_required_kes or trade.stake_kes or 1)) * 100
        trade.payout_kes = max(float(trade.margin_required_kes or trade.stake_kes or 0) + pnl, 0.0)
        price_engine.update_net_exposure(
            trade.pair,
            -float(trade.notional_value_kes or trade.stake_kes or 0),
            trade.direction == TradeDirection.LONG,
        )
        
        await db.commit()
        await db.refresh(trade)
        return trade
    
    @staticmethod
    async def get_user_trades(db: AsyncSession, user_id: str, limit: int = 50) -> list[Trade]:
        """Get user's trades."""
        normalized_user_id = TradeService._normalize_uuid(user_id)
        result = await db.execute(
            select(Trade)
            .where(Trade.user_id == normalized_user_id)
            .order_by(Trade.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_open_trades(db: AsyncSession, user_id: str) -> list[Trade]:
        """Get user's open trades."""
        normalized_user_id = TradeService._normalize_uuid(user_id)
        result = await db.execute(
            select(Trade)
            .where(and_(Trade.user_id == normalized_user_id, Trade.status == TradeStatus.OPEN))
            .order_by(Trade.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_trade_by_id(db: AsyncSession, trade_id: str) -> Trade | None:
        """Get trade by ID."""
        normalized_trade_id = TradeService._normalize_uuid(trade_id)
        result = await db.execute(select(Trade).where(Trade.id == normalized_trade_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_open_positions_snapshot(db: AsyncSession, user_id: str) -> OpenPositionsResponse:
        """Get user's open positions with live pricing and account exposure."""
        trades = await TradeService.get_open_trades(db, user_id)
        positions: list[PositionSummary] = []
        used_margin_kes = 0.0
        total_notional_kes = 0.0
        unrealized_pnl_kes = 0.0

        for trade in trades:
            current_price = TradeService.get_live_price(trade.pair)
            snapshot = TradeService.build_position_snapshot(trade, current_price)
            used_margin_kes += snapshot["margin_required_kes"]
            total_notional_kes += snapshot["notional_value_kes"]
            unrealized_pnl_kes += snapshot["unrealized_pnl_kes"]

            positions.append(
                PositionSummary(
                    id=trade.id,
                    pair=trade.pair,
                    direction=trade.direction,
                    status=trade.status,
                    stake_kes=float(trade.stake_kes),
                    leverage=snapshot["leverage"],
                    margin_required_kes=snapshot["margin_required_kes"],
                    notional_value_kes=snapshot["notional_value_kes"],
                    quantity_units=snapshot["quantity_units"],
                    open_price=float(trade.open_price),
                    current_price=snapshot["current_price"],
                    liquidation_price=snapshot["liquidation_price"],
                    unrealized_pnl_kes=snapshot["unrealized_pnl_kes"],
                    unrealized_pnl_percent=snapshot["unrealized_pnl_percent"],
                    stop_loss_kes=float(trade.stop_loss_kes) if trade.stop_loss_kes is not None else None,
                    take_profit_kes=float(trade.take_profit_kes) if trade.take_profit_kes is not None else None,
                    open_time=trade.open_time,
                )
            )

        return OpenPositionsResponse(
            open_positions=len(positions),
            used_margin_kes=round(used_margin_kes, 2),
            total_notional_kes=round(total_notional_kes, 2),
            unrealized_pnl_kes=round(unrealized_pnl_kes, 2),
            positions=positions,
        )
