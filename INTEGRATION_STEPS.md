# Real-time Analytics Integration Steps

## How to Integrate Real-time Analytics into Your Existing App

### Step 1: Update Navbar (Optional but Recommended)

In `web/index.html`, find the navbar section and add an Analytics link:

```html
<!-- Add to navigation bar -->
<a href="#" onclick="goToPage('realtime-analytics')" class="nav-link">
    📊 Analytics
</a>
```

Example location in navbar:
```html
<nav class="navbar">
    <div class="nav-left">
        <a href="#" onclick="goToPage('landing')" class="nav-brand">RJW GLOBAL FX</a>
    </div>
    <div class="nav-center">
        <a href="#" onclick="goToPage('dashboard')" class="nav-link">Dashboard</a>
        <a href="#" onclick="goToPage('analytics')" class="nav-link">Analytics</a>
        <a href="#" onclick="goToPage('realtime-analytics')" class="nav-link">📊 Real-time</a>
        <a href="#" onclick="goToPage('leaderboard')" class="nav-link">Leaderboard</a>
    </div>
    <div class="nav-right">
        <!-- existing nav items -->
    </div>
</nav>
```

### Step 2: Add Page Container

In `web/index.html`, find the pages section and add:

```html
<!-- Add after other page divs -->
<div id="page-realtime-analytics" class="page hidden">
    <!-- Analytics content loads here -->
</div>
```

Example location:
```html
<div id="page-landing" class="page"><!-- existing --></div>
<div id="page-register" class="page hidden"><!-- existing --></div>
<div id="page-login" class="page hidden"><!-- existing --></div>
<div id="page-dashboard" class="page hidden"><!-- existing --></div>
<div id="page-analytics" class="page hidden"><!-- existing --></div>
<div id="page-realtime-analytics" class="page hidden"><!-- NEW --></div>
<div id="page-leaderboard" class="page hidden"><!-- existing --></div>
<div id="page-profile" class="page hidden"><!-- existing --></div>
```

### Step 3: Update App.js Navigation

In `web/js/app.js`, find the `goToPage()` function and add a case for realtime analytics:

```javascript
function goToPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => page.classList.add('hidden'));
    
    // Show selected page
    const page = document.getElementById(`page-${pageName}`);
    if (page) {
        page.classList.remove('hidden');
    }

    // Update navbar based on auth status
    updateNavbar();

    // Load page-specific data
    switch(pageName) {
        case 'dashboard':
            if (API.isAuthenticated()) {
                loadDashboard();
            } else {
                goToPage('landing');
            }
            break;
        case 'analytics':
            if (API.isAuthenticated()) {
                loadAnalytics();
            } else {
                goToPage('landing');
            }
            break;
        case 'realtime-analytics':  // NEW
            if (API.isAuthenticated()) {
                loadRealtimeAnalytics();
            } else {
                goToPage('landing');
            }
            break;
        case 'leaderboard':
            loadLeaderboard();
            break;
        case 'profile':
            if (API.isAuthenticated()) {
                loadProfile();
            } else {
                goToPage('landing');
            }
            break;
    }

    // Scroll to top
    window.scrollTo(0, 0);
}
```

### Step 4: Add Loading Function

In `web/js/app.js`, add the function to load realtime analytics:

```javascript
// Add after other page loading functions (after loadAnalytics, etc)
async function loadRealtimeAnalytics() {
    try {
        const response = await fetch('pages/realtime-analytics.html');
        const html = await response.text();
        document.getElementById('page-realtime-analytics').innerHTML = html;
        
        // The analytics page will auto-initialize
        // (it has DOMContentLoaded handlers)
    } catch (error) {
        console.error('Error loading realtime analytics:', error);
        showError('Failed to load analytics dashboard');
    }
}
```

### Step 5: Verify API Base URL

In `web/js/api.js`, ensure `API_BASE_URL` is correctly set:

```javascript
// Check that this matches your backend URL
const API_BASE_URL = 'http://localhost:4000/api';

// Or for production
// const API_BASE_URL = 'https://your-api-domain.com/api';
```

### Step 6: Backend - Verify Routes Are Registered

In `backend/app.py`, verify these lines exist (should be added automatically):

```python
# Register blueprints
from routes.realtime_analytics_routes import realtime_analytics_routes
app.register_blueprint(realtime_analytics_routes, url_prefix='/api/analytics/realtime')
```

Should be located right after the `# ROUTES - Define after db initialization` comment.

### Step 7: Test the Integration

1. Start the backend:
```bash
cd backend
source venv/bin/activate
python app.py
```

2. Start the frontend:
```bash
cd web
python3 -m http.server 8000
```

3. Open browser:
```
http://localhost:8000
```

4. Register/Login with test account

5. Click "📊 Real-time" in navbar (or "📊 Analytics" if you named it that)

6. You should see the analytics dashboard loading

### Step 8: Test with Trade Data

1. Go to Dashboard
2. Execute a few trades (buy/sell)
3. Go back to Real-time Analytics
4. You should see:
   - Balance updated
   - Trade count increased
   - Win rate calculated
   - Pair statistics updated
   - Recent trades listed

### Step 9: Verify All Features

- [ ] Dashboard loads without errors
- [ ] Account performance metrics display
- [ ] Risk metrics show (with color-coded badges)
- [ ] Platform statistics populate
- [ ] Pair performance table shows trades
- [ ] Recent trades stream updates
- [ ] Auto-refresh toggle works
- [ ] Manual refresh button works
- [ ] Mobile responsive design works
- [ ] No console errors (F12 to check)

---

## Quick Verification Checklist

### Backend Ready?
```bash
# In backend directory
python3 -m py_compile utils/realtime_trade_analytics.py
python3 -m py_compile routes/realtime_analytics_routes.py
python3 -m py_compile app.py
```

Should produce no output (0 errors).

### API Endpoint Works?
```bash
# Start backend, then in another terminal:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:4000/api/analytics/realtime/live/user-metrics
```

Should return JSON with user metrics.

### Frontend Loads?
1. Open browser
2. Login
3. Click analytics link
4. Dashboard should load in <2 seconds

---

## Troubleshooting

### Issue: "Cannot GET /api/analytics/realtime/live/..."

**Solution:**
1. Check backend is running
2. Verify routes registered in app.py:
   ```bash
   grep "realtime_analytics_routes" backend/app.py
   ```
3. Restart backend: `python app.py`

### Issue: Dashboard shows "Loading..." forever

**Solution:**
1. Open browser console (F12)
2. Check Network tab for failed requests
3. Look for 404 or 401 errors
4. Verify token is valid (try Dashboard first)
5. Check API_BASE_URL in api.js

### Issue: Metrics show 0 or "No data"

**Solution:**
1. Execute at least one trade from Dashboard
2. Wait 1-2 seconds
3. Go back to Analytics page
4. Click Refresh button
5. Data should populate

### Issue: "Unauthorized" error

**Solution:**
1. Re-login to the app
2. Get new token
3. Try analytics again
4. Check browser localStorage for 'token' key

### Issue: Navbar link not appearing

**Solution:**
1. Verify you added the link to navbar HTML
2. Check spelling: `onclick="goToPage('realtime-analytics')"`
3. Verify page container has ID: `page-realtime-analytics`
4. Check app.js has the case statement

---

## Optional Enhancements

### 1. Add to Dashboard

Add a quick link to full analytics from Dashboard:

```javascript
// In loadDashboard() or dashboard HTML
<button onclick="goToPage('realtime-analytics')" class="btn btn-primary">
    📊 View Detailed Analytics
</button>
```

### 2. Add Performance Widget

Add small analytics widget to Dashboard header:

```html
<div class="analytics-widget">
    <div>Balance: <span id="quick-balance">$0</span></div>
    <div>P&L: <span id="quick-pnl">+$0</span></div>
    <div>Win Rate: <span id="quick-wr">0%</span></div>
</div>
```

Update with quick fetch:
```javascript
// In Dashboard
setInterval(() => {
    fetch('/api/analytics/realtime/live/user-metrics')
        .then(r => r.json())
        .then(data => {
            document.getElementById('quick-balance').textContent = 
                '$' + data.balance.toFixed(2);
            // ... update others
        });
}, 10000);
```

### 3. Add Push Notifications

Alert on risk thresholds:

```javascript
// In realtime-analytics.html
if (riskMetrics.drawdown_percent > 30) {
    showNotification('⚠️ High Drawdown Risk!', 'warning');
}

if (riskMetrics.daily_loss_remaining < 50) {
    showNotification('⚠️ Daily Loss Limit Critical!', 'danger');
}
```

### 4. Add Export Feature

Export analytics to CSV:

```javascript
function exportAnalytics() {
    const data = {
        timestamp: new Date().toISOString(),
        metrics: // ...
    };
    
    const csv = convertToCSV(data);
    downloadCSV(csv, 'analytics.csv');
}
```

### 5. Add Chart Visualization

Include Chart.js for trend charts:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Then render in realtime-analytics.html:
```javascript
const ctx = document.getElementById('trend-chart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        // ...
    }
});
```

---

## Files Modified vs Created

### Modified Files
- `backend/app.py` - Added blueprint registration (5 lines)
- (Optional) `web/index.html` - Add navbar link and page container
- (Optional) `web/js/app.js` - Add route handler

### Created Files
- `backend/utils/realtime_trade_analytics.py` - NEW
- `backend/routes/realtime_analytics_routes.py` - NEW
- `web/pages/realtime-analytics.html` - NEW
- `REALTIME_ANALYTICS_GUIDE.md` - NEW
- `REALTIME_ANALYTICS_QUICKSTART.md` - NEW
- `REALTIME_ANALYTICS_SUMMARY.md` - NEW
- `INTEGRATION_STEPS.md` - THIS FILE

---

## Next Steps After Integration

1. **Test thoroughly** with real trades
2. **Configure auto-refresh** rate for your needs
3. **Monitor performance** on your server
4. **Gather user feedback** on metrics usefulness
5. **Add export feature** if needed
6. **Implement charts** with Chart.js
7. **Add push notifications** for alerts
8. **Scale database** if needed for more users

---

## Support

- **Questions?** Check `REALTIME_ANALYTICS_GUIDE.md`
- **Setup help?** Check `REALTIME_ANALYTICS_QUICKSTART.md`
- **Implementation done?** Check `REALTIME_ANALYTICS_SUMMARY.md`

---

**Version**: 1.0.0  
**Status**: ✅ Ready to Integrate  
**Updated**: January 28, 2026
