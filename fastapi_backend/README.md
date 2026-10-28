# RJW GLOBAL FX - FastAPI Backend

**Simulated Forex Trading Platform for Kenyan University Students**

## ⚠️ Disclaimer

This is a **SIMULATED FOREX GAME FOR LEARNING & FUN ONLY**. 
- All prices are controlled by the platform
- Not connected to real forex markets
- No real profits/losses outside the app
- **Play at own risk!**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or poetry
- PostgreSQL (optional, SQLite included for development)

### Installation

1. **Clone/Setup Project**
```bash
cd fastapi_backend
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run Application**
```bash
python main.py
# OR with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Visit**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📁 Project Structure

```
fastapi_backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── trade.py      # Trade endpoints
│   │   └── health.py     # Health check
│   ├── core/             # Core configurations
│   │   ├── config.py     # Settings & environment
│   │   ├── security.py   # JWT & password utilities
│   │   └── database.py   # SQLAlchemy setup
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   ├── trade.py
│   │   └── portfolio.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   ├── trade.py
│   │   ├── portfolio.py
│   │   └── common.py
│   ├── services/         # Business logic
│   │   ├── user_service.py
│   │   └── trade_service.py
│   └── utils/            # Utilities
│       ├── logger.py
│       └── dependencies.py
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── .env.example         # Example environment
└── README.md           # This file
```

---

## 🔌 API Endpoints

### Health Check
```
GET /health
```

### Authentication
```
POST /api/auth/register    # Register new user
POST /api/auth/login       # Login user
```

### Trades
```
POST /api/trades/          # Create trade
GET /api/trades/           # Get user trades
GET /api/trades/open       # Get open trades
GET /api/trades/{id}       # Get specific trade
POST /api/trades/{id}/close # Close trade
```

---

## 🔐 Security

- JWT-based authentication
- Bcrypt password hashing
- CORS enabled for frontend (localhost:3000)
- Token expiration after 30 minutes
- SQL injection protection via SQLAlchemy ORM

---

## 💰 Forex Simulation

### Features
- **Minimum Stake**: KSh 50
- **Starting Balance**: KSh 129,500
- **Currency**: KES (Kenyan Shilling)
- **Pairs Available**: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, XAU/USD, BTC/USD
- **Price Generation**: Platform-generated with realistic volatility

### Trade Types
- **BUY (Long)**: Profit if price goes UP
- **SELL (Short)**: Profit if price goes DOWN

### Risk Management
- **Stop Loss**: Automatic trade closure at loss limit
- **Take Profit**: Automatic trade closure at profit target

---

## 📊 User Balance

All trades deduct from user balance initially:
```
User Balance Flow:
1. User created with KSh 129,500
2. Trade created → Amount deducted from balance
3. Trade closed → Amount + P&L added back
```

Example:
```
Initial Balance: KSh 129,500
Trade: BUY KSh 5,000
After Trade: KSh 124,500 (5,000 deducted)
Trade Closes (P&L: +KSh 385):
Final: KSh 129,885 (124,500 + 5,000 + 385)
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app
```

---

## 🗄️ Database Setup

### SQLite (Development)
Default, no setup needed. File: `test.db`

### PostgreSQL (Production)

1. **Create Database**
```bash
createdb rjw_global_fx
```

2. **Update .env**
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rjw_global_fx
```

3. **Run Application**
Tables created automatically on startup.

---

## 📝 Environment Variables

See `.env.example` for all available options:

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | sqlite | Database connection string |
| SECRET_KEY | dev-key | JWT secret key |
| ENVIRONMENT | development | dev/production |
| DEBUG | true | Debug mode |
| CORS_ORIGINS | localhost:3000 | Frontend URLs |
| MIN_STAKE_KES | 50 | Minimum trade amount |
| LOG_LEVEL | INFO | Logging level |

---

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Could not locate a Flask application
→ Check DATABASE_URL in .env
→ Ensure PostgreSQL is running (if using PostgreSQL)
```

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
→ pip install -r requirements.txt
→ Ensure virtual environment is activated
```

### Port Already in Use
```
ERROR: Address already in use
→ Change port: uvicorn main:app --port 8001
→ Or kill process: lsof -i :8000 && kill -9 <PID>
```

---

## 🚀 Deployment

### Docker

```dockerfile
# Build
docker build -t rjw-forex .

# Run
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... rjw-forex
```

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Use PostgreSQL
- [ ] Configure CORS_ORIGINS properly
- [ ] Use HTTPS
- [ ] Set up monitoring/logging
- [ ] Configure email service for password reset

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 👨‍💻 Development

### Contributing
1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push: `git push origin feature/amazing-feature`
4. Open Pull Request

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Format with black: `black app/`

---

## 📞 Support

- **Docs**: http://localhost:8000/docs
- **Email**: support@rwjglobalfx.edu.ke
- **Discord**: [Join Server]

---

## 📄 License

MIT License - See LICENSE file for details

---

## ✨ Features Roadmap

- [ ] Mobile app support
- [ ] Real-time price streaming (WebSocket)
- [ ] Social trading features
- [ ] Advanced analytics dashboard
- [ ] Leaderboards & competitions
- [ ] Educational content integration
- [ ] Email notifications
- [ ] Two-factor authentication

---

**Made with ❤️ for Kenyan University Students** 🚀
