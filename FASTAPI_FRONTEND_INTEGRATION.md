# FastAPI + Frontend Integration Guide

## 🎯 Integration Checklist

Your **FastAPI backend** is ready! Now integrate with the frontend.

---

## 1️⃣ Start FastAPI Backend

```bash
cd fastapi_backend
pip install -r requirements.txt
python main.py
```

**Runs on**: `http://localhost:8000`

---

## 2️⃣ Update Frontend API Configuration

### File: `/web/js/api.js`

**Current (Old Flask)**:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

**Keep as is** - FastAPI also runs on 8000! ✅

---

## 3️⃣ Frontend Endpoints Mapping

### Authentication
```javascript
// Register
POST /api/auth/register
Body: { username, email, password }

// Login
POST /api/auth/login
Body: { username, password }

// Response: { access_token, token_type, user, disclaimer }
```

### Trades
```javascript
// Create Trade
POST /api/trades/
Headers: { Authorization: "Bearer {token}" }
Body: { pair, trade_type, amount, entry_price, stop_loss, take_profit }

// Get User Trades
GET /api/trades/
Headers: { Authorization: "Bearer {token}" }

// Get Open Trades
GET /api/trades/open
Headers: { Authorization: "Bearer {token}" }

// Close Trade
POST /api/trades/{trade_id}/close?exit_price={price}
Headers: { Authorization: "Bearer {token}" }
```

---

## 4️⃣ Key Implementation Notes

### Token Storage
```javascript
// On login success
localStorage.setItem('token', response.access_token);

// On API calls
fetch('/api/...', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
```

### Response Structure
**All responses include `disclaimer`**:
```json
{
  "id": "...",
  "user": {...},
  "balance": 129500,
  "disclaimer": "This is a simulated forex game for learning & fun only..."
}
```

### Error Handling
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_001"
}
```

---

## 5️⃣ Frontend Updates Required

### File: `/web/js/app.js`

Update login handler:
```javascript
async function handleLogin(username, password) {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  // Show disclaimer
  console.log(data.disclaimer);
  
  return data;
}
```

---

## 6️⃣ Running Both Servers

### Terminal 1 - Backend
```bash
cd fastapi_backend
python main.py
# Running on http://localhost:8000
```

### Terminal 2 - Frontend
```bash
cd web
python3 -m http.server 3000
# Running on http://localhost:3000
```

**Access frontend**: http://localhost:3000

---

## 7️⃣ Database

### Current Setup
- **Type**: SQLite
- **File**: `fastapi_backend/test.db` (auto-created)
- **No setup needed** ✅

### For Production
Switch to PostgreSQL:

1. Create database:
```bash
createdb rjw_global_fx
```

2. Update `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rjw_global_fx
```

---

## 8️⃣ Testing Authentication Flow

### Register (Postman/cURL)
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teststudent",
    "email": "test@university.ac.ke",
    "password": "SecurePass123!"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "teststudent",
    "email": "test@university.ac.ke",
    "balance": 129500.0,
    "currency": "KES",
    "is_active": true,
    "created_at": "2024-01-29T12:00:00",
    "updated_at": "2024-01-29T12:00:00"
  },
  "disclaimer": "This is a simulated forex game for learning & fun only..."
}
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teststudent",
    "password": "SecurePass123!"
  }'
```

### Create Trade
```bash
curl -X POST http://localhost:8000/api/trades/ \
  -H "Authorization: Bearer eyJhbGciOi..." \
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

---

## 9️⃣ API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try all endpoints in browser!

---

## 🔟 Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 📋 Side-by-Side Comparison

| Aspect | Old Flask | New FastAPI |
|--------|-----------|-----------|
| Port | 8000 | 8000 |
| Async | ❌ | ✅ |
| ORM | SQLAlchemy | SQLAlchemy + async |
| Auth | JWT | JWT + bearer |
| Database | SQLite | SQLite → PostgreSQL |
| API Docs | ❌ | ✅ (Swagger + ReDoc) |
| Validation | Manual | Pydantic |
| Performance | Good | Better |

---

## 🚀 Next: Advanced Features

### Ready to add:
- [ ] WebSocket for live prices
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Leaderboard system
- [ ] Social features
- [ ] Mobile app support

---

## ✅ Verification Checklist

- [ ] FastAPI runs on port 8000
- [ ] Frontend runs on port 3000
- [ ] CORS enabled (localhost:3000)
- [ ] Database initialized (test.db created)
- [ ] Can register user
- [ ] Can login user
- [ ] Can create trade
- [ ] Token stored in localStorage
- [ ] Disclaimer shown in responses

---

## 🔧 Troubleshooting

### Port 8000 already in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Module not found
```bash
cd fastapi_backend
pip install -r requirements.txt
```

### Database error
```bash
# Delete old database and let it recreate
rm test.db
python main.py
```

### CORS error
Check `.env`:
```
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

---

## 📞 Support

**Issue?** Check:
1. Both servers running
2. Correct ports (8000 backend, 3000 frontend)
3. Token in localStorage
4. Network tab for API calls
5. http://localhost:8000/docs for API spec

---

## 🎓 Learning Path

1. **Understand the flow**: Registration → Login → Trade → P&L
2. **Test API endpoints** in Swagger UI
3. **Integrate frontend** step by step
4. **Add more features**: Portfolio, analytics, etc.
5. **Deploy to production**: Docker + PostgreSQL

---

**Your FastAPI backend is ready!** 🚀

Start servers and access http://localhost:3000
