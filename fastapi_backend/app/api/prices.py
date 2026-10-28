"""
Price streaming and market data endpoints
Integrates with PriceEngine for realistic simulated prices
"""

from fastapi import APIRouter, HTTPException, WebSocketDisconnect, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from app.services.price_engine import price_engine, MarketSession
from app.core.config import settings


class ExposureUpdate(BaseModel):
    """Request body for exposure updates"""
    delta: float
    is_long: bool = True

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/market", tags=["market"])

# Track active WebSocket connections per pair
ws_connections = {}


@router.get("/pairs")
async def get_available_pairs():
    """Get list of available currency pairs"""
    pairs = []
    for pair_name, config in price_engine.PAIRS_CONFIG.items():
        pairs.append({
            "pair": pair_name,
            "base_price": config.base_price,
            "volatility": config.volatility,
            "trend": config.trend,
        })
    return {"pairs": pairs, "disclaimer": settings.SIMULATION_DISCLAIMER}


@router.get("/prices")
async def get_current_prices():
    """Get latest prices for all active pairs"""
    active_sessions = {}
    for session_id, session in price_engine.sessions.items():
        if price_engine.active_sessions.get(session_id):
            active_sessions[session.pair] = session_id

    # Ensure every configured pair has an active session.
    for pair_name in price_engine.PAIRS_CONFIG.keys():
        if pair_name not in active_sessions:
            session = price_engine.start_session(pair_name)
            active_sessions[pair_name] = session.session_id

    # Advance each active session by one tick on every poll.
    for session_id in active_sessions.values():
        price_engine.generate_tick(session_id)

    prices = price_engine.get_latest_prices()
    
    return {
        "timestamp": asyncio.get_event_loop().time(),
        "prices": prices,
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


@router.get("/prices/{pair:path}")
async def get_pair_price(pair: str):
    """Get latest price for a specific pair"""
    if pair not in price_engine.PAIRS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Pair {pair} not found")

    session_id = None
    for sid, session in price_engine.sessions.items():
        if session.pair == pair and price_engine.active_sessions.get(sid):
            session_id = sid
            break

    if not session_id:
        session_id = price_engine.start_session(pair).session_id

    price_engine.generate_tick(session_id)
    prices = price_engine.get_latest_prices(pair=pair)

    return {
        "pair": pair,
        "price_data": prices[pair],
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


@router.get("/candles/{pair:path}")
async def get_pair_candles(pair: str, timeframe: str = "15m", limit: int = 120):
    """Get aggregated OHLCV candles for a pair."""
    if pair not in price_engine.PAIRS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Pair {pair} not found")

    try:
        candles = price_engine.get_candles(pair, timeframe=timeframe, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "pair": pair,
        "timeframe": timeframe,
        "candles": candles,
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }


@router.post("/session/start/{pair:path}")
async def start_market_session(pair: str):
    """Start a new market session for a pair"""
    try:
        session = price_engine.start_session(pair)
        
        # Generate initial tick
        tick = price_engine.generate_tick(session.session_id)
        
        return {
            "session_id": session.session_id,
            "pair": session.pair,
            "seed": session.seed,
            "base_price": session.base_price,
            "initial_price": tick.price if tick else session.base_price,
            "start_time": session.start_time,
            "disclaimer": settings.SIMULATION_DISCLAIMER,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_data(session_id: str):
    """Get session data including audit information"""
    data = price_engine.get_session_data(session_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data["disclaimer"] = settings.SIMULATION_DISCLAIMER
    return data


@router.post("/session/{session_id}/end")
async def end_market_session(session_id: str):
    """End a market session and reveal seed"""
    try:
        session = price_engine.end_session(session_id)
        
        return {
            "session_id": session_id,
            "seed": session.seed,  # Revealed for audit
            "pair": session.pair,
            "tick_count": len(session.ticks),
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_seconds": session.end_time - session.start_time,
            "platform_margin": session.platform_margin,
            "cumulative_bias": session.cumulative_bias,
            "message": "Session ended. Seed revealed for independent audit.",
            "disclaimer": settings.SIMULATION_DISCLAIMER,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/session/{session_id}/exposure")
async def update_pair_exposure(session_id: str, exposure: ExposureUpdate):
    """
    Update net exposure for a pair
    
    delta > 0: adding stake
    delta < 0: removing stake
    is_long: True for long position, False for short
    """
    try:
        if session_id not in price_engine.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = price_engine.sessions[session_id]
        price_engine.update_net_exposure(session.pair, exposure.delta, exposure.is_long)
        
        return {
            "pair": session.pair,
            "delta": exposure.delta,
            "is_long": exposure.is_long,
            "net_exposure": price_engine.get_net_exposure(session.pair),
            "disclaimer": settings.SIMULATION_DISCLAIMER,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# WEBSOCKET: Real-time Price Streaming
# ============================================================================

@router.websocket("/ws/prices/{pair:path}")
async def websocket_prices(websocket: WebSocket, pair: str):
    """
    WebSocket endpoint for real-time price streaming
    
    Clients connect and receive price updates every tick
    """
    await websocket.accept()
    
    if pair not in price_engine.PAIRS_CONFIG:
        await websocket.send_json({"error": f"Unknown pair: {pair}"})
        await websocket.close()
        return
    
    # Find or create session
    session_id = None
    for sid, session in price_engine.sessions.items():
        if session.pair == pair and price_engine.active_sessions.get(sid):
            session_id = sid
            break
    
    if not session_id:
        session = price_engine.start_session(pair)
        session_id = session.session_id
    
    # Track this connection
    if pair not in ws_connections:
        ws_connections[pair] = []
    ws_connections[pair].append(websocket)
    
    logger.info(f"WebSocket connected for {pair}")
    
    try:
        while True:
            # Generate new tick
            tick = price_engine.generate_tick(session_id)
            
            if tick:
                # Send to client
                await websocket.send_json({
                    "type": "price_update",
                    "pair": pair,
                    "price": tick.price,
                    "bid": tick.bid,
                    "ask": tick.ask,
                    "change": tick.change,
                    "change_percent": tick.change_percent,
                    "volume": tick.volume,
                    "timestamp": tick.timestamp,
                    "disclaimer": settings.SIMULATION_DISCLAIMER,
                })
            
            # Variable interval (1-5 seconds based on pair config)
            interval = price_engine.get_tick_interval(pair)
            await asyncio.sleep(interval)
    
    except WebSocketDisconnect:
        ws_connections[pair].remove(websocket)
        logger.info(f"WebSocket disconnected for {pair}")
    except Exception as e:
        logger.error(f"WebSocket error for {pair}: {e}")
        if websocket in ws_connections.get(pair, []):
            ws_connections[pair].remove(websocket)


@router.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for single session
    Streams all ticks for a specific market session
    """
    await websocket.accept()
    
    if session_id not in price_engine.sessions:
        await websocket.send_json({"error": f"Unknown session: {session_id}"})
        await websocket.close()
        return
    
    session = price_engine.sessions[session_id]
    
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while price_engine.active_sessions.get(session_id):
            tick = price_engine.generate_tick(session_id)
            
            if tick:
                await websocket.send_json({
                    "type": "tick",
                    "session_id": session_id,
                    "pair": session.pair,
                    "price": tick.price,
                    "bid": tick.bid,
                    "ask": tick.ask,
                    "change": tick.change,
                    "change_percent": tick.change_percent,
                    "volume": tick.volume,
                    "timestamp": tick.timestamp,
                    "tick_count": len(session.ticks),
                    "platform_margin": session.platform_margin,
                    "cumulative_bias": session.cumulative_bias,
                })
            
            # Variable interval
            interval = price_engine.get_tick_interval(session.pair)
            await asyncio.sleep(interval)
        
        # Send session end
        await websocket.send_json({
            "type": "session_end",
            "session_id": session_id,
            "seed": session.seed,
            "pair": session.pair,
            "message": "Session ended. Seed revealed.",
        })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")


@router.get("/health/market")
async def market_health():
    """Health check for market engine"""
    active_sessions = sum(1 for v in price_engine.active_sessions.values() if v)
    
    return {
        "status": "healthy" if active_sessions > 0 or not price_engine.sessions else "idle",
        "active_sessions": active_sessions,
        "total_sessions": len(price_engine.sessions),
        "pairs_configured": len(price_engine.PAIRS_CONFIG),
        "ws_connections": sum(len(v) for v in ws_connections.values()),
        "disclaimer": settings.SIMULATION_DISCLAIMER,
    }
