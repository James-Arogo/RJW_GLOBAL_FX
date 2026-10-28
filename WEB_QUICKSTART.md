# 🚀 How to Run RJW GLOBAL FX in Your Web Browser

**Complete step-by-step guide to get the platform running locally**

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites Check

```bash
# Check Python is installed
python3 --version
# Should show Python 3.8+

# Check Node/npm (optional, not needed)
# node --version

# Check you have the project files
ls ~/Desktop/RJW_GLOBAL_FX/
# Should show: backend/, web/, STUDENT_TRADING_GUIDE.md, etc.
```

---

## 📋 Step 1: Set Up Backend (Python)

### 1.1 Open Terminal/Command Prompt

**On Mac/Linux:**
```bash
# Open terminal and navigate to project
cd ~/Desktop/RJW_GLOBAL_FX/
```

**On Windows:**
```bash
# Open Command Prompt or PowerShell
cd C:\Users\YourUsername\Desktop\RJW_GLOBAL_FX\
```

### 1.2 Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**You should see `(venv)` prefix in your terminal**

### 1.3 Install Required Packages

```bash
# Go to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
```

**Expected packages:**
- Flask
- Flask-CORS
- Flask-JWT-Extended
- Flask-SocketIO
- SQLAlchemy
- python-dotenv

### 1.4 Verify Backend Installation

```bash
# Still in backend directory
python3 -c "from flask import Flask; print('✅ Flask installed')"
python3 -c "from models import db; print('✅ Models OK')"
```

---

## 🎯 Step 2: Start the Backend Server

### 2.1 Run Flask Backend

```bash
# Make sure you're in backend directory
cd backend

# Start the server
python app.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:4000
 * Debug mode: on
 * WARNING: This is a development server...
```

**✅ Backend is now running on http://localhost:4000**

### 2.2 Keep This Terminal Open

Leave this terminal running! Don't close it or the backend will stop.

---

## 🌐 Step 3: Start the Frontend Server

### 3.1 Open Another Terminal/Tab

**Keep the first terminal running the backend!**

Open a **NEW** terminal window/tab:

```bash
# Navigate to web directory
cd ~/Desktop/RJW_GLOBAL_FX/web

# On Mac/Linux:
python3 -m http.server 8000

# On Windows (same command works):
python3 -m http.server 8000
```

**Expected output:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**✅ Frontend is now running on http://localhost:8000**

---

## 🌍 Step 4: Open in Web Browser

### 4.1 Open Your Browser

Go to: **http://localhost:8000**

You should see:
- RJW GLOBAL FX landing page
- Purple gradient header
- Features listed
- "Get Started" button

### 4.2 Verify Both Servers Running

**Backend:** http://localhost:4000 (terminal 1)
**Frontend:** http://localhost:8000 (terminal 2, open in browser)

---

## 📝 Step 5: Create Your Account & Test

### 5.1 Register Account

1. Click "Register" button
2. Fill in:
   - **Username:** testuser (or your name)
   - **Email:** test@university.edu
   - **Password:** TestPass123! (must have: uppercase, number, special char)
3. Click "Register"

### 5.2 Login

1. Click "Login"
2. Enter credentials
3. You should see Dashboard with KSH 129,500 balance

### 5.3 Test Dashboard

1. Go to "Dashboard" (from navbar)
2. See live prices updating
3. See your balance in KSH
4. Try clicking "BUY" or "SELL"

### 5.4 Try Student Dashboard (NEW!)

1. Go to navbar
2. Look for "📈 Student Dashboard" (if integrated)
3. See:
   - KSH balance
   - Live prices
   - Trading tips
   - Quick trade panel
   - Recent trades

---

## 🎯 Step 6: Execute Your First Trade

### 6.1 From Student Dashboard

1. **Select Pair:** EUR/USD
2. **Direction:** Click "BUY (Long)"
3. **Amount:** Enter 5000 (KSH)
4. **Stop Loss:** Enter 500 (KSH)
5. **Take Profit:** Enter 1000 (KSH)
6. **Click:** "🚀 Execute Trade"

### 6.2 See Results

1. Check "Recent Trades" section
2. See your trade listed (green if win, red if loss)
3. Watch balance update
4. Check analytics for metrics

---

## 📊 Step 7: View Real-time Analytics

1. Click "📊 Analytics" or "📊 Real-time" in navbar
2. See:
   - Account Performance Card
   - Risk Metrics Card
   - Platform Statistics
   - Pair Comparison Table
   - Live Trade Stream
   - Performance Charts

3. Click "Refresh" to update manually
4. Toggle "Auto-refresh" to enable 10-second updates

---

## 🏆 Step 8: Check Leaderboard

1. Click "🏆 Leaderboard" in navbar
2. See top traders
3. Check your ranking
4. See win rates and earnings
5. Compete with other users (if multi-player)

---

## 🔧 Troubleshooting

### Issue: "Backend not running"

**Solution:**
```bash
# Make sure you're in backend directory
cd ~/Desktop/RJW_GLOBAL_FX/backend

# Check if port 4000 is available
# If not, change port in app.py (last line)

# Try starting again
python app.py
```

### Issue: "Frontend not loading"

**Solution:**
```bash
# Make sure you're in web directory
cd ~/Desktop/RJW_GLOBAL_FX/web

# Try a different port (e.g., 8001)
python3 -m http.server 8001

# Then visit http://localhost:8001
```

### Issue: "Cannot register account"

**Solution:**
1. Check backend is running (see terminal output)
2. Check password meets requirements (8+ chars, uppercase, number, special)
3. Check email format is valid
4. Try different username (might be taken)

### Issue: "Prices not updating"

**Solution:**
1. Refresh the page (Ctrl+R or Cmd+R)
2. Check backend is still running
3. Check browser console (F12) for errors
4. Click "🔄 Refresh" button on dashboard

### Issue: "Cannot execute trade"

**Solution:**
1. Make sure you're logged in
2. Check amount is at least 1,000 KSH
3. Check you have enough balance
4. Check Stop Loss < Take Profit
5. Try smaller amount (5,000 KSH)

---

## 📱 Access from Mobile Phone

### 1. Find Your Computer IP

**On Mac/Linux:**
```bash
ifconfig | grep inet
# Look for 192.168.x.x or 10.0.x.x
```

**On Windows:**
```bash
ipconfig
# Look for IPv4 Address (like 192.168.1.100)
```

### 2. Access from Phone

1. On your phone's browser
2. Go to: `http://YOUR_IP:8000`
3. Example: `http://192.168.1.100:8000`
4. Should work on WiFi network

### 3. Mobile Testing

- Try dashboard on phone
- Execute trades
- Check responsive design
- View student dashboard on mobile

---

## 📊 Complete Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Backend dependencies installed
- [ ] Backend running on localhost:4000
- [ ] Frontend running on localhost:8000
- [ ] Browser can access localhost:8000
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Can see balance in KSH
- [ ] Can view live prices
- [ ] Can execute a trade
- [ ] Can view analytics
- [ ] Can see leaderboard

---

## 🎓 Next Steps After Running

### 1. Read Documentation

```bash
# Read student trading guide
cat ~/Desktop/RJW_GLOBAL_FX/STUDENT_TRADING_GUIDE.md

# Read system summary
cat ~/Desktop/RJW_GLOBAL_FX/STUDENT_EDITION_SUMMARY.md
```

### 2. Explore Features

- [ ] Dashboard - Trading interface
- [ ] Analytics - Performance metrics
- [ ] Student Dashboard - Gamified interface (if integrated)
- [ ] Leaderboard - Rankings
- [ ] Profile - Account settings
- [ ] Trading Tips - Learn while using

### 3. Execute Test Trades

- [ ] Try BUY trade (EUR/USD)
- [ ] Try SELL trade (GBP/USD)
- [ ] Try different amounts
- [ ] Use Stop Loss & Take Profit
- [ ] Track your P&L

### 4. Join Competitions

- [ ] Create account with your real info
- [ ] Execute 5+ trades
- [ ] Try to reach 50%+ win rate
- [ ] Climb leaderboard
- [ ] Reach Expert level (50+ trades)

---

## 🛑 Stopping the Servers

### Stop Backend
```bash
# In the backend terminal, press:
Ctrl + C
# (or Cmd + C on Mac)
```

### Stop Frontend
```bash
# In the frontend terminal, press:
Ctrl + C
# (or Cmd + C on Mac)
```

### Closing Terminal

```bash
# Deactivate virtual environment
deactivate

# Close terminal window
```

---

## 🔄 Running Again Later

### Quick Start (Next Time)

```bash
# Terminal 1 - Backend
cd ~/Desktop/RJW_GLOBAL_FX/backend
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
python app.py

# Terminal 2 - Frontend (in new terminal)
cd ~/Desktop/RJW_GLOBAL_FX/web
python3 -m http.server 8000

# Then open browser: http://localhost:8000
```

---

## 🎯 Project Structure

```
RJW_GLOBAL_FX/
├── backend/
│   ├── app.py              ← Main Flask app
│   ├── models.py           ← Database models
│   ├── requirements.txt    ← Python dependencies
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── trade_routes.py
│   │   ├── analytics_routes.py
│   │   └── realtime_analytics_routes.py (NEW)
│   └── utils/
│       ├── live_price_engine.py (NEW)
│       ├── realtime_trade_analytics.py
│       ├── currency_converter.py
│       └── market_engine.py
│
├── web/
│   ├── index.html          ← Main page (start here)
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── api.js
│   │   └── app.js
│   └── pages/
│       ├── student-dashboard.html (NEW)
│       ├── realtime-analytics.html
│       └── ...
│
└── Documentation/
    ├── STUDENT_TRADING_GUIDE.md (NEW)
    ├── STUDENT_EDITION_SUMMARY.md (NEW)
    ├── REALTIME_ANALYTICS_GUIDE.md
    ├── WEB_QUICKSTART.md (THIS FILE)
    └── ...
```

---

## 🌟 Key URLs Once Running

| URL | Purpose |
|-----|---------|
| `http://localhost:8000` | Main app landing page |
| `http://localhost:8000/?page=dashboard` | Trading dashboard |
| `http://localhost:8000/?page=student-dashboard` | Student dashboard (new) |
| `http://localhost:8000/?page=analytics` | Analytics page |
| `http://localhost:4000/api/auth/login` | Backend login endpoint |
| `http://localhost:4000/api/trade/live_prices` | Live prices API |

---

## 💡 Tips & Tricks

### 1. Keep Servers Running
- Use separate terminal windows/tabs
- Don't close terminals while using the app
- If a server crashes, restart it

### 2. Browser Developer Tools
- Press F12 to open console
- Check Network tab for API calls
- Look for errors in Console tab
- Inspect elements in Elements tab

### 3. Database
- Located at: `backend/database.db`
- Delete it to reset all data (accounts, trades, etc.)
- Automatically created when backend starts

### 4. Testing Accounts
Create multiple test accounts:
- Student 1: `student1` / `Student1Pass!`
- Student 2: `student2` / `Student2Pass!`
- Trader: `trader1` / `Trader1Pass!`

### 5. Hard Refresh Browser
If you see old data:
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

---

## 🎯 First Time User Path

1. **Start servers** (following steps 1-3)
2. **Open browser** to localhost:8000
3. **Register account** with your email
4. **Read trading tips** on dashboard
5. **Execute first trade** (start with 1,000 KSH)
6. **View your analytics** to see performance
7. **Check leaderboard** to see rankings
8. **Execute 4-5 trades** to understand flow
9. **Read STUDENT_TRADING_GUIDE.md** for deeper learning
10. **Join competitions** and have fun! 🚀

---

## 🆘 Need Help?

### Check These First:
1. Are both servers running? (check terminal windows)
2. Is there a Python error? (read terminal output)
3. Is the port already in use? (try different port)
4. Did you activate virtual environment?
5. Did you install requirements?

### Common Ports
- Backend: 4000 (changeable)
- Frontend: 8000 (can change to 8001, 9000, etc.)

### Browser Console Errors
Press F12 in browser to see:
- JavaScript errors
- API request failures
- CORS issues
- Network problems

---

## ✅ SUCCESS INDICATORS

When everything is working:
- ✅ Backend shows "Running on http://0.0.0.0:4000"
- ✅ Frontend shows "Serving HTTP on 0.0.0.0 port 8000"
- ✅ Browser loads landing page with no errors
- ✅ Can register and login
- ✅ Dashboard shows KSH balance (129,500)
- ✅ Prices update every 2 seconds
- ✅ Can execute trades successfully
- ✅ Recent trades appear in list
- ✅ Analytics page loads with data

---

## 🎉 Ready to Start Trading!

You now have a fully functional forex trading platform running locally!

**Next:** Read [STUDENT_TRADING_GUIDE.md](STUDENT_TRADING_GUIDE.md) to learn how to trade effectively.

---

**Version:** 1.0.0  
**Last Updated:** January 28, 2026  
**Status:** ✅ Ready to Use

Happy Trading! 📈💹

