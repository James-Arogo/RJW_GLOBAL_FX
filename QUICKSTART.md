# Quick Start Guide - RJW GLOBAL FX

Get the full forex trading simulator up and running in minutes!

## 📋 Prerequisites

- Python 3.12+
- Modern web browser
- Terminal/Command line
- No additional packages needed (all included!)

## 🚀 Quick Start (5 minutes)

### Step 1: Start the Backend Server

```bash
# Navigate to backend directory
cd /path/to/RJW_GLOBAL_FX/backend

# Activate Python environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
python app.py
```

**Expected Output:**
```
[*] Environment detected: DEVELOPMENT
[*] Database: sqlite:///database.db
[*] Debug mode: True
 * Running on http://0.0.0.0:4000
```

✅ **Backend is now running on `http://localhost:4000`**

### Step 2: Start the Frontend Server

**In a new terminal:**

```bash
# Navigate to web directory
cd /path/to/RJW_GLOBAL_FX/web

# Start HTTP server (choose one):

# Option A: Python 3
python3 -m http.server 8000

# Option B: Python 2
python -m SimpleHTTPServer 8000

# Option C: Node (if installed)
npx http-server -p 8000

# Option D: Direct file open
# Just open web/index.html in your browser
```

**Expected Output:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/)
```

✅ **Frontend is now running on `http://localhost:8000`**

### Step 3: Open the Application

Open your browser and navigate to:
```
http://localhost:8000
```

You should see the RJW GLOBAL FX landing page! 🎉

## 📝 First Steps in the App

### 1. Create an Account

1. Click **"Register"** button
2. Fill in:
   - **Username**: (3-50 characters, alphanumeric + underscore/dash)
   - **Email**: (valid email address)
   - **Password**: (8+ chars, 1 uppercase, 1 digit, 1 special char)
3. Click **"Create Account"**
4. You'll be redirected to login with $1,000 virtual balance

### 2. Login

1. Enter your username and password
2. Click **"Login"**
3. You'll be taken to the **Dashboard**

### 3. Explore the Dashboard

The dashboard shows:
- **Balance**: Your current account balance
- **Total P&L**: Total profit/loss
- **Win Rate**: Percentage of winning trades
- **Trades**: Number of trades executed
- **Live Prices**: Real-time market prices
- **Trade Execution**: Form to place trades
- **Recent Trades**: History of your trades
- **Quick Stats**: Key metrics (Sharpe ratio, etc.)

### 4. Execute Your First Trade

1. Select a **Currency Pair** (e.g., EUR/USD)
2. Enter an **Amount** (e.g., $100)
3. Click **"Execute Trade"**
4. Watch the result (WIN/LOSS/NEUTRAL)
5. See your balance update in real-time

### 5. View Your Analytics

1. Click **"Analytics"** button
2. See:
   - Performance metrics
   - Risk assessment
   - Per-pair statistics
   - Professional indicators

### 6. Check the Leaderboard

1. Click **"Leaderboard"** button
2. See global trader rankings
3. Compare your performance with others

### 7. View Your Profile

1. Click your username in the navbar
2. See your account details
3. Track your statistics

## 🌐 Access Points

| Page | URL | Purpose |
|------|-----|---------|
| Landing | http://localhost:8000 | Welcome & features |
| Dashboard | http://localhost:8000#dashboard | Trading interface |
| Analytics | http://localhost:8000#analytics | Performance metrics |
| Leaderboard | http://localhost:8000#leaderboard | Global rankings |
| Profile | http://localhost:8000#profile | User info |
| API Docs | http://localhost:4000/docs | Backend documentation |

## 💡 Tips for First Trade

### Good Starting Points
- **Currency Pair**: EUR/USD (most stable)
- **Amount**: $50-$200 (test amount)
- **Strategy**: Mix of different pairs

### Risk Management
- Start small ($50-$100)
- Diversify across pairs
- Monitor Sharpe ratio
- Check win rate

### Understanding Results
- **WIN**: Trade made profit ✅
- **LOSS**: Trade made loss ❌
- **NEUTRAL**: Trade had minimal change ➖

## 📊 Key Metrics Explained

### Performance Metrics
- **Total P&L**: Sum of all profits/losses
- **Win Rate**: % of winning trades (target: 50%+)
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)
- **Profit Factor**: Ratio of wins to losses (target: 1.5+)
- **Max Drawdown**: Worst loss from peak (lower is better)

### Risk Metrics
- **Volatility**: Price movement intensity (σ)
- **VaR (95%)**: Max loss at 95% confidence
- **Expected Shortfall**: Average of worst losses
- **Risk/Reward Ratio**: Risk vs. potential gain

## 🔧 Configuration

### Backend Config
**File**: `backend/.env`

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
DATABASE_URL=sqlite:///database.db
FRONTEND_URL=http://localhost:8000
```

### Frontend Config
**File**: `web/js/api.js`

```javascript
const API_BASE_URL = 'http://localhost:4000/api';
const API_TIMEOUT = 10000;
```

## 🐛 Troubleshooting

### "Cannot POST /api/auth/login"
- ❌ Backend not running
- ✅ Start backend: `python app.py`

### "CORS error" or "Network error"
- ❌ Backend CORS not configured
- ✅ Backend has CORS enabled by default
- ✅ Ensure backend running on port 4000

### Prices not updating
- ❌ Price update interval not running
- ✅ Refresh page (F5)
- ✅ Check browser console for errors

### Trades not executing
- ❌ Insufficient balance
- ❌ Invalid pair or amount
- ✅ Check error message in UI
- ✅ Verify amount > $0.01

### Can't login after register
- ❌ Username/password mismatch
- ❌ Account not created
- ✅ Try registering again
- ✅ Check browser console for errors

## 📱 Mobile Access

The frontend is **fully responsive** and works on mobile:

1. Ensure backend is accessible from your network
2. Find your machine's IP address:
   ```bash
   # On Mac/Linux
   ifconfig | grep "inet "
   
   # On Windows
   ipconfig | findstr "IPv4"
   ```
3. Open in mobile browser: `http://<your-ip>:8000`

## 🔐 Security Notes

### Session Management
- Tokens stored in LocalStorage
- Auto-logout on page close (tokens cleared)
- Refresh tokens for extended sessions

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 digit
- At least 1 special character (!@#$%^&*)

### Best Practices
- Don't share your password
- Clear browser cache periodically
- Use strong passwords
- Logout before closing browser on shared computers

## 🎓 Learning Path

1. **Basic Trading** (5 mins)
   - Create account
   - Execute 5-10 trades
   - Understand win/loss

2. **Portfolio Management** (10 mins)
   - Diversify across pairs
   - Monitor balance changes
   - Track win rate

3. **Analytics Review** (15 mins)
   - Check Sharpe ratio
   - Review risk metrics
   - Analyze per-pair performance

4. **Leaderboard Comparison** (10 mins)
   - Compare with top traders
   - Set performance goals
   - Identify improvement areas

5. **Advanced Strategy** (ongoing)
   - Optimize trade sizing
   - Risk management
   - Pattern recognition

## 📞 Support

### Common Issues

**Q: How do I reset my balance?**
A: Delete your account from the leaderboard (not implemented yet). Contact admin.

**Q: Can I trade with real money?**
A: No, this is a simulator with $1,000 virtual balance per account.

**Q: Is my data persistent?**
A: Yes, all trades and statistics are saved in the database.

**Q: Can I have multiple accounts?**
A: Yes, each unique username = new account.

**Q: How often do prices update?**
A: Every 2 seconds on the frontend, continuous on backend.

## 🚀 Next Steps

1. ✅ Create your account
2. ✅ Execute 10 trades
3. ✅ Analyze your performance
4. ✅ Compete on leaderboard
5. ✅ Improve your strategy

## 📚 Documentation

- **Backend API**: http://localhost:4000/docs
- **Backend Guide**: `backend/README.md`
- **Frontend Guide**: `web/README.md`
- **System Improvements**: `backend/IMPROVEMENTS.md`

## 🎯 Feature Showcase

### Working Features ✅
- User registration & authentication
- Live price ticker (8 pairs)
- Trade execution
- Real-time portfolio updates
- Performance analytics
- Risk metrics
- Global leaderboard
- User profile
- Responsive UI
- Error handling

### Coming Soon 🚀
- Advanced order types (limit, stop-loss, take-profit)
- Chart visualizations
- Trade notifications
- Mobile app (Flutter)
- Social features
- Automated trading strategies

## 📊 Dashboard Stats

After executing trades, your dashboard will show:
- Current balance with P&L color coding
- Win rate percentage
- Total number of trades
- Quick stats (Sharpe, Profit Factor, Max Drawdown)
- Recent trade history
- Live price updates

## ⚡ Performance Tips

1. **Clear Cache**: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
2. **Reduce Price Updates**: Only on Dashboard (every 2 seconds)
3. **Close Unused Tabs**: Free up memory
4. **Use Chrome/Firefox**: Best performance

## 🎉 You're Ready!

You now have a fully functional forex trading simulator with:
- ✅ Modern web interface
- ✅ Real-time market data
- ✅ Professional analytics
- ✅ Global competition
- ✅ Enterprise-grade backend

**Start trading now!** 📈

---

**Questions?** Check the docs:
- API: http://localhost:4000/docs
- Backend: `backend/README.md`  
- Frontend: `web/README.md`

**Report issues:**
- Check browser console (F12)
- Verify backend running
- Check network tab in DevTools

**Enjoy!** 🚀💹

---

**Version**: 1.0.0  
**Last Updated**: January 28, 2026  
**Status**: ✅ Production Ready
