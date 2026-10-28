# Price Engine - Realistic Simulated Forex Trading

## 🎯 Overview

The **PriceEngine** service generates realistic, auditable simulated forex prices using:

- **Geometric Brownian Motion (GBM)** - Standard finance model for asset prices
- **Volatility Clustering** - Realistic vol persistence (vol tends to stay high/low)
- **Trend Following** - Prices tend to continue moving (momentum)
- **Adaptive House Bias** - Platform adjusts prices based on net exposure (capped to prevent obvious rigging)
- **Cryptographic Seeding** - All sessions seeded for independent audit/replay

---

## 📊 Mathematical Model

### Geometric Brownian Motion

```
dS/S = μ*dt + σ*dW + bias

where:
  S     = Price
  μ     = Drift (trend)
  σ     = Volatility (annualized)
  dW    = Wiener process increment (random)
  bias  = Adaptive house bias
```

**Implementation**:
```python
S_new = S_old * (1 + drift*dt + vol*dW + bias)
```

### Volatility Clustering

Volatility is not constant. It tends to persist:

```
vol(t) = α*vol(t-1) + (1-α)*mean_vol

where α ≈ 0.7 (high persistence)
```

This creates realistic "quiet" and "choppy" periods.

### Adaptive House Bias

Platform adjusts prices based on its net exposure:

```
if platform_margin < -30%:     # Platform losing money
    bias = +0.0001             # Slight upward nudge (helps shorts)
    
elif platform_margin > +30%:   # Platform winning
    bias = -0.0001             # Slight downward nudge (helps longs)
    
else:
    bias = 0.0                 # No bias
    
cap: bias <= max_bias (0.008 = 0.8%)  # Prevent obvious rigging
```

---

## 🏗️ Architecture

### Market Session

Each active pair has a **MarketSession**:

```python
@dataclass
class MarketSession:
    session_id: str              # Unique ID
    pair: str                    # "EUR/USD"
    seed: str                    # Crypto seed (hex) for audit
    start_time: float            # Unix timestamp
    base_price: float            # Starting price
    current_price: float         # Live price
    ticks: List[Tick]            # All price updates
    platform_margin: float       # Cumulative P&L
    cumulative_bias: float       # Total bias applied
    net_exposure: float          # Sum(long) - Sum(short)
```

### Tick Data

Each price update is a **Tick**:

```python
@dataclass
class Tick:
    timestamp: float             # When generated
    pair: str                    # Currency pair
    price: float                 # Mid price
    bid: float                   # Bid price
    ask: float                   # Ask price
    change: float                # Price change (absolute)
    change_percent: float        # Price change (%)
    volume: int                  # Trade volume (contracts)
```

---

## 🚀 Usage

### 1. Start a Market Session

```python
from app.services.price_engine import price_engine

session = price_engine.start_session("EUR/USD")
# Returns: MarketSession with crypto seed
# session.seed = "a1b2c3d4e5f6..." (for audit)
```

### 2. Generate Price Ticks

```python
tick = price_engine.generate_tick(session.session_id)
# Tick: price=1.0856, change=+0.0006, change_percent=+0.06%
```

### 3. Track Exposure

```python
# User places BUY order
price_engine.update_net_exposure("EUR/USD", delta=+5000)  # +5000 long

# User closes position
price_engine.update_net_exposure("EUR/USD", delta=-5000)  # Back to neutral
```

### 4. End Session & Reveal Seed

```python
session = price_engine.end_session(session.session_id)
print(f"Seed: {session.seed}")  # Revealed for audit
# Others can replay with same seed to verify prices
```

---

## 🔌 FastAPI Endpoints

### REST API

```
GET /api/market/pairs              # List all available pairs
GET /api/market/prices             # Get latest prices (all pairs)
GET /api/market/prices/{pair}      # Get price for one pair

POST /api/market/session/start/{pair}      # Start session
GET /api/market/session/{session_id}       # Get session data
POST /api/market/session/{session_id}/end  # End session (reveal seed)

POST /api/market/session/{session_id}/exposure  # Update net exposure
GET /api/market/health/market               # Engine health check
```

### Example: Start Session

```bash
curl -X POST http://localhost:8000/api/market/session/start/EUR/USD

Response:
{
  "session_id": "EUR/USD_1705084800_a1b2c3d4",
  "pair": "EUR/USD",
  "seed": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "base_price": 1.0850,
  "initial_price": 1.0856,
  "start_time": 1705084800.123
}
```

### Example: Get Prices

```bash
curl http://localhost:8000/api/market/prices

Response:
{
  "prices": {
    "EUR/USD": {
      "price": 1.0856,
      "bid": 1.0855,
      "ask": 1.0857,
      "change": +0.0006,
      "change_percent": +0.06,
      "timestamp": 1705084805.456
    },
    "GBP/USD": {...},
    ...
  }
}
```

### WebSocket: Real-time Prices

```javascript
// Subscribe to EUR/USD price updates
const ws = new WebSocket('ws://localhost:8000/api/market/ws/prices/EUR%2FUSD');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(`EUR/USD: ${msg.price} (${msg.change_percent}%)`);
};
```

### WebSocket: Session Streaming

```javascript
// Stream all ticks for a session
const ws = new WebSocket('ws://localhost:8000/api/market/ws/session/EUR%2FUSD_1705084800_a1b2c3d4');

ws.onmessage = (event) => {
  const tick = JSON.parse(event.data);
  console.log(tick);  // Full tick with all data
};
```

---

## 🔐 Audit & Transparency

### Cryptographic Seed

Every session is seeded with **128 bits of cryptographic randomness**:

```python
import secrets
seed = secrets.token_hex(16)  # 32 hex chars = 128 bits
```

This seed is revealed when the session ends.

### Independent Replay

Others can replay the session:

```python
import random

# Use revealed seed
random.seed(int(seed, 16))

# Replay: generate exact same ticks as platform
for _ in range(tick_count):
    tick = generate_tick()  # Identical to original
```

### Audit Trail

End session to get audit data:

```bash
POST /api/market/session/EUR%2FUSD_1705084800_a1b2c3d4/end

Response:
{
  "session_id": "EUR/USD_1705084800_a1b2c3d4",
  "seed": "a1b2c3d4e5f6...",           # Revealed!
  "pair": "EUR/USD",
  "tick_count": 150,
  "start_time": 1705084800.123,
  "end_time": 1705084810.456,
  "duration_seconds": 10.333,
  "platform_margin": 0.025,             # 2.5% profit
  "cumulative_bias": -0.000045,         # Small bias applied
  "message": "Session ended. Seed revealed for audit."
}
```

---

## 📈 Pair Configurations

Default pairs with realistic parameters:

| Pair | Base | Vol | Trend | Max Bias |
|------|------|-----|-------|----------|
| EUR/USD | 1.0850 | 1.2% | +0.01% | 0.8% |
| GBP/USD | 1.2750 | 1.4% | +0.02% | 0.8% |
| USD/JPY | 149.50 | 1.6% | -0.01% | 0.8% |
| USD/CHF | 0.8850 | 1.3% | 0.0% | 0.8% |
| AUD/USD | 0.6550 | 1.5% | +0.01% | 0.8% |
| USD/CAD | 1.3250 | 1.2% | 0.0% | 0.8% |
| XAU/USD | 2050.0 | 1.8% | +0.02% | 0.8% |
| BTC/USD | 42500.0 | 2.5% | +0.05% | 0.8% |

Customize in `PAIRS_CONFIG`:

```python
class PriceEngine:
    PAIRS_CONFIG = {
        'EUR/USD': PriceConfig(
            pair='EUR/USD',
            base_price=1.0850,
            volatility=0.012,      # 1.2% daily
            trend=0.0001,          # +0.01% daily drift
            max_bias=0.008,        # Max 0.8% bias
        ),
        # ...
    }
```

---

## ⚙️ Background Task

**Periodic Bias Adjustment** runs every **5 minutes**:

```python
async def adjust_bias_periodically(interval=300):
    """
    Every 5 min:
    1. Calculate platform margin from recent trades
    2. Recompute adaptive bias
    3. Log margin and bias for transparency
    """
    while True:
        for session in active_sessions:
            margin = calculate_platform_margin(session)
            bias = compute_house_bias(margin)
            # Apply bias in next tick generation
        await asyncio.sleep(interval)
```

Bias is **recalculated every 5 ticks** within generate_tick(), but rechecked against margin history every 5 minutes.

---

## 🎓 Key Features

### ✅ Realistic Price Movement

- **GBM Model** - Industry standard (Black-Scholes, etc.)
- **Vol Clustering** - Matches real forex behavior
- **Bid-Ask Spread** - Proportional to volatility
- **Volume** - Random but consistent

### ✅ Transparent Bias

- **Capped** at 0.8% max to prevent obvious rigging
- **Adaptive** only when platform margin is extreme
- **Revealed** at session end for audit
- **Logged** for compliance

### ✅ Auditable

- **Cryptographic Seed** - Deterministic for replay
- **Session Data** - All ticks stored
- **Margin Tracking** - Platform P&L visible
- **Bias History** - Cumulative bias logged

### ✅ Scalable

- **Per-pair Sessions** - Independent market simulations
- **WebSocket Streaming** - Real-time updates
- **Memory-efficient** - Sliding window of recent ticks
- **Async** - Non-blocking background tasks

---

## 🔍 Example: Trading Scenario

```python
from app.services.price_engine import price_engine

# 1. Start session
session = price_engine.start_session("EUR/USD")
print(f"Seed: {session.seed}")

# 2. Generate 100 ticks (1-2 seconds each)
for i in range(100):
    tick = price_engine.generate_tick(session.session_id)
    print(f"Tick {i}: {tick.price} ({tick.change_percent:+.2f}%)")

# 3. User place BUY order
price_engine.update_net_exposure("EUR/USD", delta=+5000)

# 4. More ticks (bias may adjust because user is now long)
for i in range(50):
    tick = price_engine.generate_tick(session.session_id)
    # If platform is losing money, slight upward bias to help users

# 5. User closes position
price_engine.update_net_exposure("EUR/USD", delta=-5000)

# 6. End session
session = price_engine.end_session(session.session_id)

# 7. Audit: verify with seed
print(f"Seed revealed: {session.seed}")
print(f"Platform margin: {session.platform_margin:.2%}")
print(f"Total bias applied: {session.cumulative_bias:.6f}")
```

---

## 🛠️ Customization

### Adjust Volatility

```python
# Make EUR/USD more volatile
PAIRS_CONFIG['EUR/USD'].volatility = 0.025  # 2.5% (higher)
```

### Change Bias Threshold

```python
# Be more aggressive with bias
if platform_margin < -0.20:  # Instead of -0.30
    bias = 0.0001
```

### Adjust Bias Update Frequency

```python
# Bias updates every 1 minute instead of 5
bias_adjustment_interval = 60  # seconds
```

### Store Ticks to Database

```python
# Modify generate_tick() to also save to database
async def save_tick(tick):
    db_tick = DBTick(...)
    db.add(db_tick)
    await db.commit()
```

---

## 📊 Monitoring

### Check Engine Health

```bash
curl http://localhost:8000/api/market/health/market

Response:
{
  "status": "healthy",
  "active_sessions": 8,
  "total_sessions": 24,
  "pairs_configured": 8,
  "ws_connections": 5
}
```

### View Session Data

```bash
curl http://localhost:8000/api/market/session/EUR%2FUSD_1705084800_a1b2c3d4

Response:
{
  "session_id": "EUR/USD_1705084800_a1b2c3d4",
  "tick_count": 150,
  "platform_margin": 0.025,
  "cumulative_bias": -0.000045,
  "first_price": 1.0850,
  "last_price": 1.0876,
  "duration_seconds": 150.5
}
```

---

## 🎓 Educational Value

Students learn:

- **Stochastic Processes** - How prices are modeled
- **Transparency** - How to audit trading platforms
- **Risk Management** - How bias affects outcomes
- **Real-world Finance** - Actual forex trading mechanics

---

## ⚠️ Disclaimer

**THIS IS A SIMULATED GAME:**

- Prices are generated by the platform
- Not connected to real forex markets
- House bias is capped and transparent
- For educational purposes only
- No real money is involved

---

## 📚 References

- **Geometric Brownian Motion**: https://en.wikipedia.org/wiki/Geometric_Brownian_motion
- **Black-Scholes Model**: Standard finance pricing model
- **Volatility Clustering**: Common empirical feature of financial time series
- **Cryptographic Randomness**: Python `secrets` module

---

**Ready to trade!** 🚀📈
