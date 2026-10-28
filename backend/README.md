# RJW GLOBAL FX Backend

A comprehensive forex trading simulation platform backend built with Flask, featuring real-time trading, advanced analytics, and professional monitoring.

## Features

### Core Features
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Real-time Trading**: Live market prices with WebSocket support
- **Advanced Orders**: Limit orders, stop-loss, and take-profit functionality
- **Portfolio Analytics**: Comprehensive performance metrics and risk analysis
- **API Documentation**: Complete Swagger/OpenAPI documentation

### Advanced Features
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Logging System**: Multi-level logging with rotation and monitoring
- **Docker Support**: Full containerization with docker-compose
- **Rate Limiting**: API protection with Nginx reverse proxy
- **Monitoring**: Prometheus and Grafana integration

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (for production)
- Redis (for caching)

### Development Setup

1. **Clone and setup**
```bash
git clone <repository-url>
cd RJW_GLOBAL_FX/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:4000`

### Docker Setup

1. **Build and run with docker-compose**
```bash
docker-compose up -d
```

2. **Access services**
- API: `http://localhost:4000`
- API Documentation: `http://localhost:4000/api/docs/swagger`
- Grafana: `http://localhost:3000` (admin/admin123)
- Prometheus: `http://localhost:9090`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/logout` - User logout

### Trading
- `GET /api/trade/live_prices` - Get live market prices
- `POST /api/trade/trade` - Execute trade
- `GET /api/trade/history/{username}` - Get trade history
- `GET /api/trade/portfolio/{username}` - Get portfolio statistics

### Advanced Orders
- `POST /api/orders/limit` - Create limit order
- `POST /api/orders/stop_loss` - Create stop-loss order
- `POST /api/orders/take_profit` - Create take-profit order
- `DELETE /api/orders/cancel/{id}` - Cancel order
- `GET /api/orders/list` - List user orders

### Analytics
- `GET /api/analytics/user/performance` - User performance metrics
- `GET /api/analytics/user/risk` - Risk metrics
- `GET /api/analytics/platform/statistics` - Platform statistics
- `GET /api/analytics/market/sentiment` - Market sentiment
- `GET /api/analytics/user/leaderboard` - User leaderboard

### Admin
- `GET /api/admin/status` - System status

## WebSocket Events

Connect to `/socket.io/` for real-time updates:

- `price_update` - Live price updates
- `trade_update` - Trade execution updates
- `order_executed` - Order execution notifications

## Testing

Run the test suite:
```bash
pytest tests/ -v --cov=.
```

Run specific test files:
```bash
pytest tests/test_auth.py -v
pytest tests/test_trade.py -v
pytest tests/test_models.py -v
```

## Configuration

### Environment Variables
- `FLASK_ENV` - Environment (development/production/testing)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## Monitoring & Logging

### Logs
- `logs/app.log` - General application logs
- `logs/errors.log` - Error logs
- `logs/security.log` - Security events (JSON format)
- `logs/trading.log` - Trading events (JSON format)
- `logs/performance.log` - Performance metrics

### Metrics
- Prometheus metrics available at `/metrics`
- Grafana dashboards for visualization
- Custom performance tracking

## Security Features

- JWT token authentication with refresh tokens
- Rate limiting on all API endpoints
- CORS protection
- Request logging and monitoring
- SQL injection protection (SQLAlchemy)
- Password hashing with Werkzeug

## Performance Features

- Redis caching for session management
- Database connection pooling
- Request/response compression
- Static file serving optimization
- Background task processing

## Development

### Code Structure
```
backend/
├── app.py              # Main application
├── config.py           # Configuration management
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── routes/             # API routes
│   ├── auth_routes.py
│   ├── trade_routes.py
│   ├── admin_routes.py
│   ├── order_routes.py
│   ├── analytics_routes.py
│   └── socketio_routes.py
├── utils/              # Utility modules
│   ├── market_engine.py
│   ├── profit_manager.py
│   ├── order_manager.py
│   ├── analytics_engine.py
│   └── logger.py
├── tests/              # Test suite
├── logs/               # Log files
└── Docker/             # Docker configuration
```

### Adding New Features
1. Create routes in appropriate route files
2. Add models to `models.py`
3. Write tests in `tests/` directory
4. Update API documentation
5. Add logging and monitoring

## Production Deployment

### Docker Production
```bash
# Set production environment
export FLASK_ENV=production

# Deploy with docker-compose
docker-compose -f docker-compose.yml up -d
```

### Manual Production
1. Set up PostgreSQL database
2. Configure Redis
3. Set environment variables
4. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:4000 app:app
```

## License

© 2024 RJW GLOBAL FX. All rights reserved.

## Support

For technical support, please contact the development team.
