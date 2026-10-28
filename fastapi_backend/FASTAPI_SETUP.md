# FastAPI Backend - Setup & Configuration Guide

## ✅ Project Created Successfully!

Complete FastAPI project structure has been created at:
```
/home/james-arogo/Desktop/RJW_GLOBAL_FX/fastapi_backend/
```

---

## 📦 What's Included

### Core Files
- ✅ `main.py` - FastAPI application with CORS, middleware, lifespan events
- ✅ `requirements.txt` - All dependencies (FastAPI, SQLAlchemy, Pydantic, etc.)
- ✅ `.env` - Environment variables (development mode)
- ✅ `.env.example` - Environment template for reference
- ✅ `pyproject.toml` - Project metadata and build configuration
- ✅ `Dockerfile` - Docker containerization
- ✅ `README.md` - Comprehensive documentation

### Project Structure

```
app/
├── api/                          # API route handlers
│   ├── auth.py                   # POST /api/auth/register, /api/auth/login
│   ├── trade.py                  # CRUD operations for trades
│   └── health.py                 # GET /health endpoint
│
├── core/                         # Core application logic
│   ├── config.py                 # Settings (Pydantic BaseSettings)
│   ├── security.py               # JWT token & password hashing
│   └── database.py               # SQLAlchemy async setup
│
├── models/                       # SQLAlchemy ORM models
│   ├── user.py                   # User (id, username, email, balance, etc.)
│   ├── trade.py                  # Trade (pair, type, amount, P&L, status)
│   └── portfolio.py              # Portfolio (statistics & metrics)
│
├── schemas/                      # Pydantic validation schemas
│   ├── user.py                   # UserCreate, LoginRequest, UserResponse, TokenResponse
│   ├── trade.py                  # TradeCreate, TradeResponse
│   ├── portfolio.py              # PortfolioResponse
│   └── common.py                 # HealthResponse, MessageResponse, ErrorResponse
│
├── services/                     # Business logic layer
│   ├── user_service.py           # User CRUD & authentication
│   └── trade_service.py          # Trade operations & P&L calculation
│
└── utils/                        # Utilities
    ├── logger.py                 # Logging configuration
    └── dependencies.py           # JWT authentication dependency
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd fastapi_backend
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```

Or with auto-reload:
```bash
uvicorn main:app --reload
```

### 3. Access Application
- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔑 Key Features

### ✅ Authentication
```python
# JWT-based authentication
POST /api/auth/register  # Register new user
POST /api/auth/login     # Login and get token
```

**Response includes**:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {...},
  "disclaimer": "This is a simulated forex game..."
}
```

### ✅ Trade Management
```python
POST /api/trades/          # Create trade (deducts balance)
GET /api/trades/           # Get all user trades
GET /api/trades/open       # Get open trades only
POST /api/trades/{id}/close # Close trade (updates balance)
```

### ✅ Security
- **Password Hashing**: Bcrypt via passlib
- **JWT Tokens**: 30-minute expiration
- **CORS**: Configured for localhost:3000 (frontend)
- **SQL Injection Protection**: SQLAlchemy ORM

### ✅ Database
- **Development**: SQLite (auto-created: `test.db`)
- **Production**: PostgreSQL + asyncpg
- **ORM**: SQLAlchemy with async support
- **Auto-migration**: Tables created on startup

### ✅ Simulation Disclaimer
Every relevant response includes:
```json
{
  "disclaimer": "This is a simulated forex game for learning & fun only. 
                Prices are controlled by the platform. 
                Not connected to real forex markets. 
                Play at own risk – no real profits/losses outside the app."
}
```

---

## 💰 Forex Trading Details

### Constants (in `app/core/config.py`)
```python
MIN_STAKE_KES = 50.0              # Minimum trade amount
STARTING_BALANCE_KES = 129_500.0  # User starting balance
CURRENCY = "KES"                  # Kenyan Shilling
```

### Available Pairs (in `app/services/trade_service.py`)
```python
EUR/USD  → 1.0850
GBP/USD  → 1.2750
USD/JPY  → 149.50
USD/CHF  → 0.8850
AUD/USD  → 0.6550
USD/CAD  → 1.3250
XAU/USD  → 2050.00 (Gold)
BTC/USD  → 42500.00 (Bitcoin)
```

### Trade Flow
1. **Create Trade**: Deducts amount from user balance
2. **Trade Opens**: Market price is simulated
3. **Trade Closes**: P&L calculated
4. **Balance Updated**: Original amount + P&L credited back

**Example**:
```
User Balance: KSh 129,500
Create Trade: BUY 5,000 KSH
Balance After: 124,500

Trade Closes with P&L: +385 KSH
Final Balance: 129,885
  = 124,500 (remaining) + 5,000 (returned) + 385 (profit)
```

---

## 📊 Data Models

### User Model
```python
{
  "id": UUID,
  "username": str,
  "email": str,
  "password_hash": str,
  "balance": float,              # In KES
  "currency": str,               # "KES"
  "is_active": bool,
  "is_admin": bool,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Trade Model
```python
{
  "id": UUID,
  "user_id": UUID,
  "pair": str,                   # "EUR/USD"
  "trade_type": Enum,            # "BUY" | "SELL"
  "amount": float,               # In KES
  "entry_price": float,
  "exit_price": float,           # null if open
  "stop_loss": float,
  "take_profit": float,
  "status": Enum,                # "OPEN" | "CLOSED" | "CANCELLED"
  "pnl": float,                  # Profit/Loss in KES
  "pnl_percent": float,          # P&L as percentage
  "created_at": datetime,
  "closed_at": datetime          # null if open
}
```

### Portfolio Model
```python
{
  "id": UUID,
  "user_id": UUID,
  "total_trades": int,
  "winning_trades": int,
  "losing_trades": int,
  "total_pnl": float,            # Cumulative P&L
  "win_rate": float,             # Percentage
  "average_win": float,
  "average_loss": float,
  "max_win": float,
  "max_loss": float,
  "daily_pnl": float,
  "monthly_pnl": float,
  "level": int,                  # 1-10+ based on performance
  "badge": str,                  # "Beginner", "Silver Trader", etc.
  "created_at": datetime,
  "updated_at": datetime
}
```

---

## 🔌 API Examples

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student123",
    "email": "student@university.ac.ke",
    "password": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student123",
    "password": "SecurePass123!"
  }'
```

### Create Trade
```bash
curl -X POST "http://localhost:8000/api/trades/" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "EUR/USD",
    "trade_type": "BUY",
    "amount": 5000.0,
    "entry_price": 1.0850,
    "stop_loss": 500.0,
    "take_profit": 1000.0
  }'
```

### Get User Trades
```bash
curl -X GET "http://localhost:8000/api/trades/" \
  -H "Authorization: Bearer {token}"
```

---

## 🗄️ Database Setup

### SQLite (Current - Development)
- Automatically created at `test.db`
- No configuration needed
- Good for testing and development

### PostgreSQL (Production)

1. **Install PostgreSQL**:
```bash
brew install postgresql  # macOS
sudo apt-get install postgresql  # Linux
```

2. **Create Database**:
```bash
createdb rjw_global_fx
```

3. **Update `.env`**:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rjw_global_fx
```

4. **Run Application**:
Tables are created automatically on startup.

---

## 📝 Environment Variables

### Current Setup (`.env`)
```bash
# Database (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./test.db

# Security
SECRET_KEY=dev-secret-key-change-in-production-1234567890
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
ENVIRONMENT=development
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"]

# Logging
LOG_LEVEL=INFO
```

### Production Checklist
- [ ] Change `SECRET_KEY` to cryptographically random value
- [ ] Set `DEBUG=false`
- [ ] Switch to PostgreSQL
- [ ] Update `CORS_ORIGINS` to production URLs
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure backups

---

## 🧪 Testing

### Run Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Test Example
```python
# tests/test_auth.py
@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
```

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t rjw-forex:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/rjw_global_fx \
  rjw-forex:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: rjw_global_fx
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:secure_password@db:5432/rjw_global_fx
      SECRET_KEY: your-secret-key
    depends_on:
      - db

volumes:
  postgres_data:
```

---

## 🚨 Troubleshooting

### "No module named fastapi"
```bash
pip install -r requirements.txt
source venv/bin/activate  # Ensure venv is active
```

### "Address already in use :8000"
```bash
lsof -i :8000
kill -9 <PID>
# OR use different port
uvicorn main:app --port 8001
```

### "Database connection refused"
```bash
# Ensure PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux

# Or use SQLite (default)
```

### "JWT token expired"
```
Get new token by logging in again
Token expiration: 30 minutes (configurable in .env)
```

---

## 📚 Next Steps

1. **Integrate with Frontend**:
   - Update frontend API_BASE_URL to `http://localhost:8000/api`
   - Handle JWT token in localStorage

2. **Add More Features**:
   - WebSocket for real-time prices
   - Email notifications
   - Advanced analytics
   - Leaderboards

3. **Production Deployment**:
   - Switch to PostgreSQL
   - Set up CI/CD pipeline
   - Configure monitoring
   - Enable rate limiting

4. **Security Hardening**:
   - Add 2FA
   - Implement refresh tokens
   - Add rate limiting
   - Set up CORS properly

---

## 📞 Support

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: Check logs in `logs/` directory

---

**Created with ❤️ for Kenyan University Students** 🚀
