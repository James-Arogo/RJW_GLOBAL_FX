# SQLAlchemy 2.x PostgreSQL Models Documentation

## 🎯 Overview

Production-ready SQLAlchemy 2.x async models for RJW GLOBAL FX platform.

**All currency in KES (Kenyan Shilling)**

---

## 📊 Data Models

### 1. User Model

```python
class User(Base):
    """User account with virtual balance in KES"""
    
    id: UUID                          # Primary key
    username: str (unique)            # Login username
    email: str (unique)               # Email address
    password_hash: str                # Bcrypt hash
    balance_kes: Numeric(15,2)        # Virtual balance (default: 10,000 KES)
    is_active: bool                   # Account active flag
    is_verified: bool                 # Email verified flag
    is_admin: bool                    # Admin role
    created_at: DateTime              # Registration time
    updated_at: DateTime              # Last update
    verified_at: DateTime (nullable)  # Email verification time
    last_login: DateTime (nullable)   # Last login time
```

**Relationships**:
- `trades`: One-to-Many relationship with Trade
- `audit_logs`: One-to-Many relationship with AuditLog

**Indexes**:
- `username` (unique)
- `email` (unique)
- `created_at` (for new user queries)

**Example**:
```python
user = User(
    username="jemo",
    email="student@university.ac.ke",
    password_hash=hash_password("SecurePass123!"),
    balance_kes=10000.00,
    is_verified=False
)
```

---

### 2. Trade Model

```python
class Trade(Base):
    """Individual trade record with complete lifecycle"""
    
    id: UUID                          # Primary key
    user_id: UUID (FK)                # User who placed trade
    pair: str                         # Currency pair (e.g., "EUR/USD")
    direction: Enum                   # "long" or "short"
    stake_kes: Numeric(12,2)          # Trade amount (min 50 KES)
    
    # Entry Side
    open_price: Numeric(15,6)         # Entry price
    open_time: DateTime               # Entry timestamp
    
    # Exit Side
    close_price: Numeric(15,6) (nullable)   # Exit price
    close_time: DateTime (nullable)         # Exit timestamp
    duration_seconds: Integer (nullable)    # Trade duration
    
    # Status
    status: Enum                      # open, closed, or cancelled
    
    # Outcomes (in KES)
    payout_kes: Numeric(12,2) (nullable)    # Total payout (stake + profit)
    profit_kes: Numeric(12,2) (nullable)    # Pure profit/loss
    profit_percent: Numeric(6,2) (nullable) # ROI %
    
    # Risk Management
    stop_loss_kes: Numeric(12,2) (nullable)      # Stop loss
    take_profit_kes: Numeric(12,2) (nullable)    # Take profit
    risk_reward_ratio: Numeric(6,2) (nullable)   # TP:SL ratio
    
    # References
    market_session_id: UUID (nullable) FK    # Associated market session
    
    # Timestamps
    created_at: DateTime              # Trade creation
    updated_at: DateTime              # Last update
```

**Relationships**:
- `user`: Many-to-One with User
- `market_session`: Many-to-One with MarketSession (optional)

**Indexes**:
- `user_id` (find user's trades)
- `pair` (find trades on a pair)
- `user_id + pair` (find user's trades on specific pair)
- `status` (find open/closed trades)
- `created_at` (sort by date)

**Example**:
```python
trade = Trade(
    user_id=user_id,
    pair="EUR/USD",
    direction=TradeDirection.LONG,
    stake_kes=5000.00,
    open_price=1.0850,
    open_time=datetime.utcnow(),
    stop_loss_kes=500.00,
    take_profit_kes=1000.00,
    status=TradeStatus.OPEN
)
```

---

### 3. MarketSession Model

```python
class MarketSession(Base):
    """Market session for price generation and audit trail"""
    
    id: UUID                          # Primary key
    pair: str                         # Currency pair
    
    # Timing
    start_time: DateTime              # Session start
    end_time: DateTime (nullable)     # Session end
    
    # Cryptographic Audit
    seed_hash: str                    # SHA-256 hash (hidden seed)
    seed_reveal: str (nullable)       # Actual seed (revealed after session)
    
    # Configuration
    engine_params: JSONB (nullable)   # {volatility, drift, base_price, max_bias}
    
    # Price Data
    base_price: Numeric(15,6)         # Starting price
    final_price: Numeric(15,6) (nullable)  # Ending price
    price_change_percent: Numeric(6,2) (nullable)
    
    # Platform Metrics
    platform_margin_kes: Numeric(12,2)  # Platform profit/loss during session
    cumulative_bias: Numeric(10,6)      # Total bias applied
    net_exposure_kes: Numeric(12,2)     # Net long/short exposure
    
    # Statistics
    tick_count: Integer               # Number of price ticks generated
    avg_volatility: Numeric(6,4) (nullable)
    
    # Status
    is_active: bool                   # Session still running
    
    # Timestamps
    created_at: DateTime              # Session creation
    updated_at: DateTime              # Last update
```

**Relationships**:
- `trades`: One-to-Many with Trade
- All trades during session reference this session

**Indexes**:
- `pair` (find sessions for a pair)
- `start_time` (sort by date)

**Audit Trail Example**:
```python
session = MarketSession(
    pair="EUR/USD",
    start_time=datetime.utcnow(),
    seed_hash="a1b2c3d4e5f6g7h8...",  # Hidden during session
    engine_params={
        "volatility": 0.012,
        "drift": 0.0001,
        "base_price": 1.0850,
        "max_bias": 0.008
    },
    base_price=1.0850,
    platform_margin_kes=0.0,
    net_exposure_kes=0.0,
    is_active=True
)

# After session ends
session.end_time = datetime.utcnow()
session.seed_reveal = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"  # Reveal seed
session.is_active = False
```

---

### 4. PlatformMetric Model

```python
class PlatformMetric(Base):
    """Daily platform-wide analytics"""
    
    id: UUID                          # Primary key
    metric_date: DateTime             # Date of metric (indexed)
    
    # Volume (KES)
    daily_staked_kes: Numeric(15,2)       # Today's total stakes
    total_staked_kes: Numeric(18,2)       # Cumulative stakes
    
    # Payout (KES)
    daily_payout_kes: Numeric(15,2)       # Today's total payouts
    total_payout_kes: Numeric(18,2)       # Cumulative payouts
    
    # Platform Profit (KES)
    daily_platform_profit_kes: Numeric(15,2)    # Today's profit
    total_platform_profit_kes: Numeric(18,2)    # Cumulative profit
    
    # Trade Statistics
    total_trades_opened: Integer      # Cumulative opens
    total_trades_closed: Integer      # Cumulative closes
    avg_trade_duration_seconds: Integer (nullable)
    
    # Win/Loss
    total_winning_trades: Integer     # Cumulative wins
    total_losing_trades: Integer      # Cumulative losses
    platform_win_rate_percent: Numeric(5,2) (nullable)
    
    # Risk
    max_concurrent_exposure_kes: Numeric(15,2) (nullable)
    avg_concurrent_exposure_kes: Numeric(15,2) (nullable)
    
    # Users
    active_users: Integer             # Daily active
    new_users: Integer                # New registrations today
    verified_users: Integer           # Email verified count
    
    # Timestamps
    created_at: DateTime
    updated_at: DateTime
```

**Use Cases**:
- Dashboard metrics
- Compliance reporting
- Platform profitability analysis

**Example**:
```python
metric = PlatformMetric(
    metric_date=datetime.utcnow(),
    daily_staked_kes=50000.00,
    daily_payout_kes=48500.00,
    daily_platform_profit_kes=1500.00,
    total_winning_trades=245,
    total_losing_trades=155,
    active_users=156
)
```

---

### 5. AuditLog Model

```python
class AuditLog(Base):
    """Immutable audit trail for compliance"""
    
    id: UUID                          # Primary key
    user_id: UUID (nullable) FK       # User involved (if applicable)
    
    # Event
    event_type: Enum                  # Event category
    event_description: str            # Human-readable description
    
    # Related Resources
    trade_id: UUID (nullable) FK      # Associated trade
    market_session_id: UUID (nullable) FK  # Associated session
    
    # Data
    event_data: JSONB (nullable)      # Additional context
    previous_value: str (nullable)    # Before change
    new_value: str (nullable)         # After change
    
    # Session Info
    ip_address: str (nullable)        # Source IP
    user_agent: str (nullable)        # Browser/client info
    
    # Timestamp (immutable)
    created_at: DateTime              # Event time
```

**Event Types**:
```
USER_REGISTERED      - User created account
USER_VERIFIED        - Email verified
TRADE_OPENED         - Trade placed
TRADE_CLOSED         - Trade closed
TRADE_CANCELLED      - Trade cancelled
BALANCE_UPDATED      - Balance changed
SESSION_STARTED      - Price session started
SESSION_ENDED        - Price session ended
SEED_REVEALED        - Audit seed revealed
BIAS_ADJUSTED        - House bias adjusted
```

**Example**:
```python
audit = AuditLog(
    user_id=user_id,
    event_type=AuditEventType.TRADE_OPENED,
    event_description="User opened EUR/USD BUY trade for 5000 KES",
    trade_id=trade_id,
    market_session_id=session_id,
    event_data={
        "pair": "EUR/USD",
        "direction": "long",
        "stake_kes": 5000.0,
        "open_price": 1.0850
    },
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)
```

---

## 🔑 Key Features

### ✅ Currency: KES (Kenyan Shilling)

All monetary values in KES:
- User balance: 10,000 KES default
- Trade stakes: minimum 50 KES
- Payouts and profits: in KES
- Platform metrics: in KES

### ✅ Numeric Precision

Using `Numeric(precision, scale)`:
- `Numeric(15, 2)` - Up to 15 digits, 2 decimal places (amounts)
- `Numeric(18, 2)` - For cumulative/total fields
- `Numeric(15, 6)` - For prices (6 decimal places)
- `Numeric(6, 2)` - For percentages

### ✅ Student-Friendly Fields

- `is_verified` - Email verification status
- `verified_at` - When email was verified
- `last_login` - Track engagement
- `balance_kes` - Clear KES-based balance
- `profit_percent` - Easy ROI understanding

### ✅ Comprehensive Audit Trail

AuditLog tracks:
- Every user action
- Trade lifecycle
- Platform events
- Balance changes
- Seed reveals (for compliance)

### ✅ Performance Indexes

Optimized queries on:
- User lookups (username, email)
- Trade filtering (user_id, pair, status)
- Time-based queries (created_at)
- Session management (pair, date)

### ✅ Relationships

```
User (1) ──→ Trade (Many)
     ├──→ AuditLog (Many)
     
MarketSession (1) ──→ Trade (Many)
              ├──→ AuditLog (Many)
              
Trade ──→ MarketSession (optional)
      ──→ User
```

---

## 🏗️ Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance_kes NUMERIC(15,2) DEFAULT 10000.00,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    verified_at DATETIME,
    last_login DATETIME
);

CREATE INDEX ix_users_username ON users(username);
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_created_at ON users(created_at);
```

### Trades Table

```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    pair VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    stake_kes NUMERIC(12,2) NOT NULL,
    open_price NUMERIC(15,6) NOT NULL,
    open_time DATETIME NOT NULL,
    close_price NUMERIC(15,6),
    close_time DATETIME,
    duration_seconds INTEGER,
    status VARCHAR(20) NOT NULL,
    payout_kes NUMERIC(12,2),
    profit_kes NUMERIC(12,2),
    profit_percent NUMERIC(6,2),
    stop_loss_kes NUMERIC(12,2),
    take_profit_kes NUMERIC(12,2),
    risk_reward_ratio NUMERIC(6,2),
    market_session_id UUID REFERENCES market_sessions(id),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_trades_user_id ON trades(user_id);
CREATE INDEX ix_trades_pair ON trades(pair);
CREATE INDEX ix_trades_user_pair ON trades(user_id, pair);
CREATE INDEX ix_trades_status ON trades(status);
CREATE INDEX ix_trades_created_at ON trades(created_at);
```

### Market Sessions Table

```sql
CREATE TABLE market_sessions (
    id UUID PRIMARY KEY,
    pair VARCHAR(20) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    seed_hash VARCHAR(64) NOT NULL,
    seed_reveal VARCHAR(64),
    engine_params JSONB,
    base_price NUMERIC(15,6) NOT NULL,
    final_price NUMERIC(15,6),
    price_change_percent NUMERIC(6,2),
    platform_margin_kes NUMERIC(12,2) DEFAULT 0.0,
    cumulative_bias NUMERIC(10,6) DEFAULT 0.0,
    net_exposure_kes NUMERIC(12,2) DEFAULT 0.0,
    tick_count INTEGER DEFAULT 0,
    avg_volatility NUMERIC(6,4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_market_sessions_pair ON market_sessions(pair);
CREATE INDEX ix_market_sessions_start_time ON market_sessions(start_time);
```

### Platform Metrics Table

```sql
CREATE TABLE platform_metrics (
    id UUID PRIMARY KEY,
    metric_date DATETIME NOT NULL,
    daily_staked_kes NUMERIC(15,2) DEFAULT 0.0,
    total_staked_kes NUMERIC(18,2) DEFAULT 0.0,
    daily_payout_kes NUMERIC(15,2) DEFAULT 0.0,
    total_payout_kes NUMERIC(18,2) DEFAULT 0.0,
    daily_platform_profit_kes NUMERIC(15,2) DEFAULT 0.0,
    total_platform_profit_kes NUMERIC(18,2) DEFAULT 0.0,
    total_trades_opened INTEGER DEFAULT 0,
    total_trades_closed INTEGER DEFAULT 0,
    avg_trade_duration_seconds INTEGER,
    total_winning_trades INTEGER DEFAULT 0,
    total_losing_trades INTEGER DEFAULT 0,
    platform_win_rate_percent NUMERIC(5,2),
    max_concurrent_exposure_kes NUMERIC(15,2),
    avg_concurrent_exposure_kes NUMERIC(15,2),
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    verified_users INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_platform_metrics_date ON platform_metrics(metric_date);
```

### Audit Logs Table

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    event_description VARCHAR(500) NOT NULL,
    trade_id UUID REFERENCES trades(id),
    market_session_id UUID REFERENCES market_sessions(id),
    event_data JSONB,
    previous_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME NOT NULL
);

CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX ix_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at);
```

---

## 💾 Usage Examples

### Create User

```python
from app.models import User
from app.core.security import hash_password

user = User(
    username="jemo",
    email="jemo@university.ac.ke",
    password_hash=hash_password("SecurePass123!"),
    balance_kes=10000.00,
    is_verified=False
)
session.add(user)
await session.commit()
```

### Open Trade

```python
from app.models import Trade, TradeDirection, TradeStatus

trade = Trade(
    user_id=user.id,
    pair="EUR/USD",
    direction=TradeDirection.LONG,
    stake_kes=5000.00,
    open_price=1.0850,
    open_time=datetime.utcnow(),
    stop_loss_kes=500.00,
    take_profit_kes=1000.00,
    status=TradeStatus.OPEN,
    market_session_id=session_id
)
session.add(trade)
await session.commit()
```

### Close Trade

```python
trade.close_price = 1.0900
trade.close_time = datetime.utcnow()
trade.duration_seconds = int((trade.close_time - trade.open_time).total_seconds())
trade.status = TradeStatus.CLOSED
trade.payout_kes = trade.stake_kes + 385.00
trade.profit_kes = 385.00
trade.profit_percent = (385.00 / 5000.00) * 100

# Update user balance
user.balance_kes += trade.profit_kes

session.add(trade)
session.add(user)
await session.commit()
```

### Log Audit Event

```python
from app.models import AuditLog, AuditEventType

audit = AuditLog(
    user_id=user.id,
    event_type=AuditEventType.TRADE_CLOSED,
    event_description=f"Closed EUR/USD LONG trade with {trade.profit_kes} KES profit",
    trade_id=trade.id,
    event_data={
        "profit_kes": float(trade.profit_kes),
        "profit_percent": float(trade.profit_percent)
    },
    ip_address="192.168.1.1"
)
session.add(audit)
await session.commit()
```

---

## 🔒 Data Constraints

### Foreign Key Constraints

- `Trade.user_id` → `User.id` (required)
- `Trade.market_session_id` → `MarketSession.id` (optional)
- `AuditLog.user_id` → `User.id` (optional)
- `AuditLog.trade_id` → `Trade.id` (optional)
- `AuditLog.market_session_id` → `MarketSession.id` (optional)

### Unique Constraints

- `User.username` (unique)
- `User.email` (unique)

### CHECK Constraints (recommended)

```sql
-- Trade must have minimum stake
ALTER TABLE trades ADD CONSTRAINT check_min_stake
  CHECK (stake_kes >= 50.00);

-- User balance can't be negative
ALTER TABLE users ADD CONSTRAINT check_min_balance
  CHECK (balance_kes >= 0);

-- Trade close_time must be after open_time (if set)
ALTER TABLE trades ADD CONSTRAINT check_trade_times
  CHECK (close_time IS NULL OR close_time > open_time);
```

---

## ✨ Summary

**Production-ready models with**:
- ✅ KES currency support
- ✅ Complete audit trail
- ✅ Trade lifecycle tracking
- ✅ Platform analytics
- ✅ Cryptographic session seeding
- ✅ Performance indexes
- ✅ Student-friendly fields
- ✅ Compliance ready

Ready for deployment! 🚀
