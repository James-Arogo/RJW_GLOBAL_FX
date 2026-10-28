# RJW GLOBAL FX - Web Frontend

A modern, interactive web frontend for the RJW GLOBAL FX forex trading simulator platform.

## Features

### 🎨 **User Interface**
- Clean, modern design with dark theme
- Responsive layout (mobile, tablet, desktop)
- Smooth animations and transitions
- Real-time price updates
- Interactive trading interface

### 💱 **Trading Features**
- Live market prices for 8 currency pairs
- One-click trade execution
- Trade history tracking
- Real-time portfolio updates
- Virtual balance management

### 📊 **Analytics & Insights**
- Comprehensive performance metrics
- Sharpe ratio calculation
- Win rate tracking
- Risk metrics (VaR, expected shortfall)
- Per-pair performance breakdown
- Maximum drawdown analysis
- Profit factor tracking

### 🏆 **Social & Competitive**
- Global leaderboard
- User ranking system
- Performance comparison
- Trader statistics

### 🔒 **Security**
- JWT authentication
- Secure token management
- Protected API endpoints
- Session management
- Password validation

### ⚡ **Performance**
- Fast page loads
- Efficient data fetching
- Minimal dependencies
- Optimized CSS
- Vanilla JavaScript (no frameworks)

## Project Structure

```
web/
├── index.html           # Main HTML structure
├── css/
│   ├── styles.css      # Main stylesheet (1000+ lines)
│   └── tailwind.min.css # Tailwind utilities
├── js/
│   ├── api.js          # Backend API handler
│   └── app.js          # Main application logic
├── assets/             # Images, icons, etc.
└── README.md           # This file
```

## Getting Started

### Prerequisites
- Backend server running on `http://localhost:4000`
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No build process needed!

### Installation

1. **Ensure backend is running:**
```bash
cd backend
source venv/bin/activate
python app.py
# Server running on http://localhost:4000
```

2. **Open frontend in browser:**
```bash
# Option 1: Direct file open (local)
open web/index.html

# Option 2: Simple HTTP server (recommended)
cd web
python3 -m http.server 8000
# Navigate to http://localhost:8000
```

### Quick Start

1. **Register account:**
   - Click "Register" button
   - Enter username, email, password
   - Account created with $1,000 virtual balance

2. **Start trading:**
   - Navigate to Dashboard
   - Select currency pair
   - Enter trade amount
   - Click "Execute Trade"

3. **View analytics:**
   - Click "Analytics" button
   - View performance metrics
   - Check risk analysis

4. **Check leaderboard:**
   - View global rankings
   - Compare with other traders

## API Integration

### Endpoints Used

#### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get user profile

#### Trading
- `GET /api/trade/live_prices` - Get current prices
- `POST /api/trade/trade` - Execute trade
- `GET /api/trade/history/{username}` - Get trade history
- `GET /api/trade/portfolio/{username}` - Get portfolio stats

#### Analytics
- `GET /api/analytics/user/performance` - Performance metrics
- `GET /api/analytics/user/risk` - Risk metrics
- `GET /api/analytics/user/leaderboard` - Global leaderboard

## Features by Page

### 🏠 Landing Page
- Platform overview
- Feature highlights
- Call-to-action buttons
- Benefits explanation

### 📝 Auth Pages
- User registration
- Login form
- Email validation
- Password strength requirements
- Error handling

### 📊 Dashboard
- Real-time price ticker
- Account statistics (balance, P&L, win rate)
- Trade execution form
- Recent trades table
- Quick analytics preview

### 📈 Analytics Page
- Performance metrics
  - Total P&L
  - Win rate
  - Sharpe ratio
  - Profit factor
  - Max drawdown
  - Largest win/loss
  
- Risk metrics
  - Volatility
  - Value at Risk (VaR)
  - Expected Shortfall
  - Risk/Reward ratio
  - Average win/loss

- Performance by pair (coming soon)

### 🏆 Leaderboard
- Global trader rankings
- Performance comparison
- Balance tracking
- Win rate statistics
- Trade volume

### 👤 Profile Page
- User information
- Account statistics
- Balance display
- Member since date
- Total trades
- Win rate

## Styling

### Color Scheme
- **Primary:** #2a5298 (Dark Blue)
- **Secondary:** #00d9ff (Cyan)
- **Success:** #28a745 (Green)
- **Danger:** #dc3545 (Red)
- **Background:** #0f1419 (Dark)
- **Cards:** #1a202c (Card Background)

### Design Principles
- Dark mode for eye comfort
- High contrast for readability
- Smooth animations
- Responsive design
- Accessible color palette

## JavaScript Code Structure

### API Handler (`api.js`)
```javascript
// Singleton instance
const API = new APIHandler();

// Methods
API.register(username, email, password)
API.login(username, password)
API.executeTrade(pair, amount)
API.getPerformanceMetrics()
API.getRiskMetrics()
API.getLeaderboard()
// ... and more
```

### App Logic (`app.js`)
- Page navigation
- Dashboard management
- Trade execution
- Analytics loading
- Leaderboard display
- Profile management
- Utility functions

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimizations

1. **Minimal Dependencies**
   - No jQuery
   - No framework overhead
   - Pure vanilla JavaScript

2. **Efficient CSS**
   - Single stylesheet
   - Minimal selectors
   - Hardware-accelerated animations

3. **Smart Data Loading**
   - Lazy loading
   - Interval-based updates
   - Efficient API calls

4. **Frontend Caching**
   - LocalStorage for tokens
   - Previous prices cached
   - Session persistence

## Responsive Design

### Mobile (< 768px)
- Single column layout
- Stacked forms
- Touch-friendly buttons
- Optimized tables

### Tablet (768px - 1024px)
- 2-3 column layouts
- Balanced spacing
- Readable fonts

### Desktop (> 1024px)
- Full 3-column layouts
- Optimal whitespace
- Enhanced visualizations

## Security Features

### Authentication
- JWT tokens in localStorage
- Bearer token headers
- Token refresh mechanism
- Logout functionality

### Data Protection
- HTTPS ready
- No sensitive data in console
- Secure password validation
- XSS prevention

### Error Handling
- User-friendly error messages
- No system details exposed
- Graceful degradation
- Timeout handling

## Future Enhancements

1. **Charts & Graphs**
   - Performance charts
   - Price history graphs
   - Analytics visualizations

2. **Advanced Orders**
   - Limit orders
   - Stop-loss orders
   - Take-profit orders

3. **Notifications**
   - Trade alerts
   - Price alerts
   - Achievement notifications

4. **Settings**
   - User preferences
   - Display options
   - API rate limits

5. **Social Features**
   - User profiles
   - Follow traders
   - Comment on trades

6. **Mobile App**
   - React Native app
   - iOS & Android
   - Push notifications

## Development

### Adding New Features

1. **New API Endpoint:**
```javascript
// In api.js
async newEndpoint() {
    return this.request('/endpoint/path', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}
```

2. **New Page:**
```html
<!-- In index.html -->
<div id="page-newpage" class="page hidden">
    <!-- Content -->
</div>

<!-- In app.js -->
case 'newpage':
    loadNewPage();
    break;
```

3. **New Styling:**
```css
/* In styles.css */
.new-element {
    /* Styles */
}
```

## Troubleshooting

### CORS Errors
- Ensure backend is running
- Check API_BASE_URL in api.js
- Backend should have CORS enabled

### Login Issues
- Clear browser cache/localStorage
- Check network tab in DevTools
- Verify credentials match backend

### Price Not Updating
- Check WebSocket connection
- Verify API endpoint working
- Check browser console for errors

## Testing API Endpoints

```bash
# Test registration
curl -X POST http://localhost:4000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Test live prices
curl http://localhost:4000/api/trade/live_prices

# Test leaderboard
curl http://localhost:4000/api/analytics/user/leaderboard
```

## Contributing

To contribute improvements:

1. Test all changes locally
2. Maintain responsive design
3. Follow existing code style
4. Update documentation
5. Test on multiple browsers

## License

© 2024 RJW GLOBAL FX. All rights reserved.

## Support

For issues or questions:
- Check browser console for errors
- Review API documentation at `/docs`
- Check backend logs
- Test with cURL first

---

**Frontend Status**: ✅ Production Ready  
**Last Updated**: January 28, 2026  
**Version**: 1.0.0
