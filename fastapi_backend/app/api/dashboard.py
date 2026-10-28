"""
Dashboard endpoints - Display model data to frontend
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models import User, Trade, TradeStatus, PlatformMetric, AuditLog, AuditEventType
from app.services.trade_service import TradeService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ============================================================================
# USER DASHBOARD
# ============================================================================

@router.get("/user/summary")
async def get_user_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user dashboard summary"""
    
    # Get user's trades
    stmt = select(Trade).where(Trade.user_id == current_user.id)
    result = await db.execute(stmt)
    trades = result.scalars().all()
    
    # Calculate statistics
    total_trades = len(trades)
    closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]
    open_trades = [t for t in trades if t.status == TradeStatus.OPEN]
    
    winning_trades = [t for t in closed_trades if t.profit_kes and t.profit_kes > 0]
    losing_trades = [t for t in closed_trades if t.profit_kes and t.profit_kes < 0]
    
    win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
    
    total_profit = sum(float(t.profit_kes or 0) for t in closed_trades)
    avg_profit = total_profit / len(closed_trades) if closed_trades else 0
    
    # Daily profit (today's closed trades)
    from datetime import datetime
    today = datetime.utcnow().date()
    today_trades = [
        t for t in closed_trades
        if t.close_time and t.close_time.date() == today
    ]
    daily_profit = sum(float(t.profit_kes or 0) for t in today_trades)
    open_positions = await TradeService.get_open_positions_snapshot(db, str(current_user.id))
    equity_kes = float(current_user.balance_kes) + float(open_positions.unrealized_pnl_kes)
    
    return {
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "balance_kes": float(current_user.balance_kes),
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat(),
        },
        "statistics": {
            "total_trades": total_trades,
            "open_trades": len(open_trades),
            "closed_trades": len(closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_percent": round(win_rate, 2),
        },
        "profitability": {
            "total_profit_kes": round(total_profit, 2),
            "average_profit_kes": round(avg_profit, 2),
            "daily_profit_kes": round(daily_profit, 2),
            "daily_return_percent": round((daily_profit / float(current_user.balance_kes) * 100), 2) if current_user.balance_kes else 0,
        },
        "account": {
            "balance_kes": float(current_user.balance_kes),
            "equity_kes": round(equity_kes, 2),
            "used_margin_kes": open_positions.used_margin_kes,
            "total_notional_kes": open_positions.total_notional_kes,
            "unrealized_pnl_kes": open_positions.unrealized_pnl_kes,
        },
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


# ============================================================================
# RECENT TRADES
# ============================================================================

@router.get("/user/trades")
async def get_user_trades(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's recent trades"""
    
    stmt = (
        select(Trade)
        .where(Trade.user_id == current_user.id)
        .order_by(Trade.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    trades = result.scalars().all()
    
    return {
        "trades": [
            {
                "id": str(trade.id),
                "pair": trade.pair,
                "direction": trade.direction.value,
                "stake_kes": float(trade.stake_kes),
                "open_price": float(trade.open_price),
                "close_price": float(trade.close_price) if trade.close_price else None,
                "status": trade.status.value,
                "profit_kes": float(trade.profit_kes) if trade.profit_kes else None,
                "profit_percent": float(trade.profit_percent) if trade.profit_percent else None,
                "duration_seconds": trade.duration_seconds,
                "open_time": trade.open_time.isoformat(),
                "close_time": trade.close_time.isoformat() if trade.close_time else None,
            }
            for trade in trades
        ],
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


@router.get("/user/open-trades")
async def get_open_trades(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's open trades"""
    
    stmt = (
        select(Trade)
        .where(
            (Trade.user_id == current_user.id) &
            (Trade.status == TradeStatus.OPEN)
        )
        .order_by(Trade.created_at.desc())
    )
    result = await db.execute(stmt)
    trades = result.scalars().all()
    
    positions = await TradeService.get_open_positions_snapshot(db, str(current_user.id))
    payload = positions.model_dump()
    payload["disclaimer"] = settings.SIMULATION_DISCLAIMER
    return payload


# ============================================================================
# PLATFORM ANALYTICS
# ============================================================================

@router.get("/platform/metrics")
async def get_platform_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get today's platform metrics"""
    
    from datetime import datetime
    today = datetime.utcnow().date()
    
    stmt = (
        select(PlatformMetric)
        .where(
            select(1)
            .select_from(PlatformMetric)
            .where(PlatformMetric.metric_date >= today)
        )
        .order_by(PlatformMetric.metric_date.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    metric = result.scalar_one_or_none()
    
    if not metric:
        # Return zeros if no metric today
        return {
            "date": today.isoformat(),
            "metrics": {
                "daily_staked_kes": 0,
                "daily_payout_kes": 0,
                "daily_platform_profit_kes": 0,
                "total_staked_kes": 0,
                "active_users": 0,
                "new_users": 0,
            },
            "disclaimer": settings.SIMULATION_DISCLAIMER,
        }
    
    return {
        "date": metric.metric_date.date().isoformat(),
        "metrics": {
            "daily_staked_kes": float(metric.daily_staked_kes),
            "daily_payout_kes": float(metric.daily_payout_kes),
            "daily_platform_profit_kes": float(metric.daily_platform_profit_kes),
            "total_staked_kes": float(metric.total_staked_kes),
            "total_winning_trades": metric.total_winning_trades,
            "total_losing_trades": metric.total_losing_trades,
            "platform_win_rate_percent": float(metric.platform_win_rate_percent) if metric.platform_win_rate_percent else 0,
            "active_users": metric.active_users,
            "new_users": metric.new_users,
        },
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


# ============================================================================
# AUDIT LOG
# ============================================================================

@router.get("/user/audit")
async def get_user_audit_log(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's audit log"""
    
    stmt = (
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {
        "audit_logs": [
            {
                "id": str(log.id),
                "event_type": log.event_type.value,
                "event_description": log.event_description,
                "event_data": log.event_data,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


# ============================================================================
# LEADERBOARD
# ============================================================================

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get top traders by profit"""
    
    # Get all closed trades with profit
    stmt = (
        select(Trade)
        .where(
            (Trade.status == TradeStatus.CLOSED) &
            (Trade.profit_kes.isnot(None))
        )
        .order_by(Trade.created_at.desc())
    )
    result = await db.execute(stmt)
    all_trades = result.scalars().all()
    
    # Group by user and calculate totals
    user_stats = {}
    for trade in all_trades:
        if str(trade.user_id) not in user_stats:
            user_stats[str(trade.user_id)] = {
                "total_profit": 0,
                "trade_count": 0,
                "user_id": str(trade.user_id)
            }
        user_stats[str(trade.user_id)]["total_profit"] += float(trade.profit_kes or 0)
        user_stats[str(trade.user_id)]["trade_count"] += 1
    
    # Sort by profit and get user details
    sorted_stats = sorted(
        user_stats.items(),
        key=lambda x: x[1]["total_profit"],
        reverse=True
    )
    
    leaderboard = []
    for idx, (user_id, stats) in enumerate(sorted_stats[:limit]):
        # Get user details
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if user:
            leaderboard.append({
                "rank": idx + 1,
                "username": user.username,
                "total_profit_kes": round(stats["total_profit"], 2),
                "trade_count": stats["trade_count"],
                "avg_profit_kes": round(stats["total_profit"] / stats["trade_count"], 2),
            })
    
    return {
        "leaderboard": leaderboard,
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def dashboard_health(db: AsyncSession = Depends(get_db)):
    """Dashboard health check"""
    
    try:
        # Try to count users
        stmt = select(User)
        result = await db.execute(stmt)
        user_count = len(result.scalars().all())
        
        # Try to count trades
        trade_stmt = select(Trade)
        trade_result = await db.execute(trade_stmt)
        trade_count = len(trade_result.scalars().all())
        
        return {
            "status": "healthy",
            "database": "connected",
            "models_integrated": True,
            "user_count": user_count,
            "trade_count": trade_count,
            "disclaimer": settings.SIMULATION_DISCLAIMER,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
