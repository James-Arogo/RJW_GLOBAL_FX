# RJW GLOBAL FX - React Web Frontend

**Modern, Student-Friendly Simulated Forex Trading Application**

Built with **Vite + React + Tailwind CSS**

---

## ⚠️ DISCLAIMER

🎮 **This is a SIMULATED GAME for learning & fun only!**

- Prices are controlled by the platform
- Not connected to real forex markets
- No real profits/losses outside the app
- Educational purpose only

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or pnpm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

**Access**: http://localhost:3000

---

## 📁 Project Structure

```
web_react/
├── src/
│   ├── pages/              # Page components
│   │   ├── Home.jsx       # Landing page
│   │   ├── Login.jsx      # Login form
│   │   ├── Register.jsx   # Registration form
│   │   ├── Dashboard.jsx  # Main dashboard (balance, P&L, stats)
│   │   ├── Trade.jsx      # Trade execution form
│   │   ├── Market.jsx     # Live market prices
│   │   └── Profile.jsx    # User profile
│   │
│   ├── components/         # Reusable components
│   │   ├── Navbar.jsx      # Navigation bar
│   │   ├── DisclaimerBanner.jsx  # Persistent disclaimer
│   │   ├── BalanceCard.jsx # Balance display
│   │   └── StatCard.jsx    # Statistics card
│   │
│   ├── context/            # React Context
│   │   └── AuthContext.jsx # Auth state management
│   │
│   ├── utils/              # Utility functions
│   │   ├── api.js          # Axios API client
│   │   └── formatting.js   # Format KES, dates, P&L
│   │
│   ├── App.jsx             # Main app + routing
│   ├── main.jsx            # Entry point
│   └── index.css           # Tailwind + custom styles
│
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
└── README.md              # This file
```

---

## 🎨 Features

### ✅ Authentication
- User registration with password validation
- JWT token-based login
- Persistent session (localStorage)
- Protected routes

### ✅ Dashboard
- Account balance in KES
- Daily P&L tracking
- Win rate calculation
- Trading statistics
- Recent trades list
- Quick action buttons

### ✅ Trading
- 8 currency pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- Buy/Sell trade directions
- Stop Loss & Take Profit setup
- Risk calculation (2% rule)
- Trade execution form

### ✅ Market
- Live simulated price updates
- Real-time volatility
- Trending indicators
- Market information

### ✅ Profile
- User information display
- Account balance
- Trading statistics
- Logout functionality

### ✅ UI/UX
- Dark theme (student-friendly)
- Blue/Green accents
- Mobile responsive
- Persistent disclaimer banner
- KES currency formatting
- Smooth animations

---

## 🔌 API Integration

### Backend Configuration

Update `.env`:
```
VITE_API_URL=http://localhost:8000/api
```

### Endpoints

```
POST /api/auth/register    # User registration
POST /api/auth/login       # User login
POST /api/trades/          # Create trade
GET /api/trades/           # Get user trades
GET /api/trades/open       # Get open trades
GET /api/health            # Health check
```

---

## 💱 Currency Formatting

All amounts are displayed in **KES** (Kenyan Shilling):

```javascript
import { formatCurrency, formatPercent } from './utils/formatting'

formatCurrency(129500, 0)  // "KES 129,500"
formatCurrency(5500.5, 2)  // "KES 5,500.50"
formatPercent(58.3)        // "58.30%"
```

---

## 🔐 Authentication Flow

1. **Register** → Create account with username, email, password
2. **Login** → Receive JWT token
3. **Store** → Token saved to localStorage
4. **Persist** → Session survives page refresh
5. **Protected Routes** → Redirects unauthenticated users to login

```javascript
// Usage in components
import { useAuth } from './context/AuthContext'

const MyComponent = () => {
  const { user, token, isAuthenticated, logout } = useAuth()
  
  // Use auth state
}
```

---

## 📱 Mobile Responsive

- Fully responsive grid layouts
- Mobile-optimized navigation
- Touch-friendly buttons
- Responsive forms
- Mobile-first design

---

## 🎯 Disclaimer Banner

Persistent banner on all pages showing:
- ⚠️ SIMULATED GAME warning
- Clear disclaimer text
- Closeable (but reminder on each visit)

---

## 🛠️ Customization

### Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  primary: { ... },    // Blue (main brand)
  success: { ... },    // Green (profits)
  warning: { ... },    // Yellow (neutral)
  // ...
}
```

### Fonts

Update in `index.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=...');
```

### Trading Pairs

Edit pairs in `Trade.jsx`:

```javascript
const pairs = [
  { value: 'EUR/USD', label: 'EUR/USD' },
  // Add more...
]
```

---

## 🚀 Deployment

### Build Production

```bash
npm run build
# Creates dist/ folder
```

### Deploy Options

**Vercel**
```bash
npm i -g vercel
vercel
```

**Netlify**
```bash
npm i -g netlify-cli
netlify deploy --prod
```

**GitHub Pages**
```bash
npm run build
# Push dist/ to gh-pages branch
```

### Environment Variables

Create `.env.production`:
```
VITE_API_URL=https://your-backend.com/api
```

---

## 📊 State Management

### Auth Context
- User data
- JWT token
- Login/logout functions
- Authentication state

### Component State
- Form data (React useState)
- Loading states
- Error messages
- Success notifications

---

## 🔍 Available Scripts

```bash
npm run dev      # Start dev server (http://localhost:3000)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
npm run format   # Format code with Prettier
```

---

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
# Use different port
npm run dev -- --port 3001
```

### API connection issues
1. Check backend is running on 8000
2. Verify `.env` API_URL
3. Check CORS headers in backend
4. Look at browser Network tab

### Styles not loading
```bash
# Rebuild Tailwind
npm run dev
# Clear node_modules
rm -rf node_modules && npm install
```

### Login not working
1. Ensure backend is running
2. Check email format
3. Verify password requirements
4. Check browser console for errors

---

## 📚 Learning Resources

- [React Documentation](https://react.dev)
- [Vite Guide](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Axios](https://axios-http.com)

---

## 🎓 For Students

This frontend demonstrates:
- ✅ Modern React patterns
- ✅ Component architecture
- ✅ State management
- ✅ API integration
- ✅ Responsive design
- ✅ Form handling
- ✅ Authentication flows
- ✅ CSS utilities (Tailwind)

Perfect for learning web development! 🚀

---

## 📞 Support

- Check `.env.example` for configuration
- Review error messages in browser console
- Verify backend API is running
- Check Network tab for API calls

---

## 📄 License

MIT - See LICENSE file

---

**Made with ❤️ for Kenyan University Students** 🎓📈

Remember: This is a **simulated game** for learning only. No real trading is happening!
