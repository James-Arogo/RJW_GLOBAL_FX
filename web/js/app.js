/**
 * RJW GLOBAL FX - Main Application Logic
 */

let priceUpdateInterval;
let analyticsUpdateInterval;
const EXCHANGE_RATE_USD_TO_KSH = 129.50;

// ========== PAGE NAVIGATION ==========

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
        case 'student-dashboard':
            if (API.isAuthenticated()) {
                loadStudentDashboard();
            } else {
                goToPage('landing');
            }
            break;
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

function updateNavbar() {
    const isAuthenticated = API.isAuthenticated();
    const loginBtn = document.getElementById('nav-login');
    const registerBtn = document.getElementById('nav-register');
    const logoutBtn = document.getElementById('nav-logout');
    const usernameDisplay = document.getElementById('username-display');

    if (isAuthenticated) {
        loginBtn?.classList.add('hidden');
        registerBtn?.classList.add('hidden');
        logoutBtn?.classList.remove('hidden');
        usernameDisplay?.classList.remove('hidden');
        document.getElementById('user-name').textContent = API.username;
    } else {
        loginBtn?.classList.remove('hidden');
        registerBtn?.classList.remove('hidden');
        logoutBtn?.classList.add('hidden');
        usernameDisplay?.classList.add('hidden');
    }
}

// ========== AUTHENTICATION ==========

// Password validation requirements
function validatePasswordRequirements(password) {
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        digit: /\d/.test(password),
        special: /[!@#$%^&*]/.test(password)
    };
    return requirements;
}

// Update password requirement indicators
function updatePasswordRequirements(password) {
    const reqs = validatePasswordRequirements(password);
    
    const elements = {
        'req-length': reqs.length,
        'req-upper': reqs.uppercase,
        'req-digit': reqs.digit,
        'req-special': reqs.special
    };

    Object.entries(elements).forEach(([id, isValid]) => {
        const el = document.getElementById(id);
        if (el) {
            if (isValid) {
                el.classList.add('valid');
                el.classList.remove('invalid');
            } else {
                el.classList.remove('valid');
                el.classList.add('invalid');
            }
        }
    });
}

// Add real-time password validation
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('register-password');
    if (passwordInput) {
        passwordInput.addEventListener('input', (e) => {
            updatePasswordRequirements(e.target.value);
        });
    }
});

// Check if all password requirements are met
function isPasswordValid(password) {
    const reqs = validatePasswordRequirements(password);
    return reqs.length && reqs.uppercase && reqs.digit && reqs.special;
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    const submitBtn = document.getElementById('register-submit');
    const btnText = document.getElementById('register-btn-text');
    const spinner = document.getElementById('register-spinner');

    // Clear previous messages
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');

    // Validate inputs
    if (username.length < 3) {
        errorDiv.textContent = '❌ Username must be at least 3 characters';
        errorDiv.classList.remove('hidden');
        return;
    }

    if (!email.includes('@')) {
        errorDiv.textContent = '❌ Please enter a valid email address';
        errorDiv.classList.remove('hidden');
        return;
    }

    if (!isPasswordValid(password)) {
        errorDiv.textContent = '❌ Password does not meet requirements';
        errorDiv.classList.remove('hidden');
        return;
    }

    try {
        // Show loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Creating...';
        spinner.classList.remove('hidden');

        const response = await API.register(username, email, password);
        
        // Show success message
        successDiv.textContent = '✅ Account created! Redirecting to login...';
        successDiv.classList.remove('hidden');
        
        // Clear form
        event.target.reset();
        
        // Redirect to login after a short delay
        setTimeout(() => {
            // Pre-fill login form
            document.getElementById('login-username').value = username;
            goToPage('login');
        }, 2000);
    } catch (error) {
        const errorMessage = error.message || 'Registration failed. Please try again.';
        errorDiv.textContent = '❌ ' + errorMessage;
        errorDiv.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Create Account';
        spinner.classList.add('hidden');
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const successDiv = document.getElementById('login-success');
    const submitBtn = document.querySelector('#login-form button[type="submit"]');
    const btnText = document.getElementById('login-btn-text');
    const spinner = document.getElementById('login-spinner');

    // Clear previous messages
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');

    // Validate inputs
    if (!username || !password) {
        errorDiv.textContent = '❌ Please enter both username and password';
        errorDiv.classList.remove('hidden');
        return;
    }

    try {
        // Show loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Logging in...';
        spinner.classList.remove('hidden');

        await API.login(username, password);
        
        // Show success message
        successDiv.textContent = '✅ Login successful! Loading your dashboard...';
        successDiv.classList.remove('hidden');
        
        // Clear form
        event.target.reset();
        
        // Redirect to dashboard
        setTimeout(() => goToPage('dashboard'), 1500);
    } catch (error) {
        const errorMessage = error.message || 'Login failed. Please check your credentials.';
        errorDiv.textContent = '❌ ' + errorMessage;
        errorDiv.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Login';
        spinner.classList.add('hidden');
    }
}

function logout() {
    if (confirm('🚪 Are you sure you want to logout?')) {
        API.logout();
        goToPage('landing');
        showSuccess('✅ Logged out successfully');
    }
}

// ========== DASHBOARD ==========

async function loadDashboard() {
    try {
        showLoading();

        // Load profile and analytics
        const [profile, portfolio, history] = await Promise.all([
            API.getProfile(),
            API.getPortfolio(),
            API.getTradeHistory()
        ]);

        // Update stats
        updateDashboardStats(profile.data, portfolio.data);
        updateRecentTrades(history.data);
        loadLivePrices();

        // Start live price updates
        if (priceUpdateInterval) clearInterval(priceUpdateInterval);
        priceUpdateInterval = setInterval(loadLivePrices, 2000);

        // Load analytics summary
        loadDashboardAnalytics();
    } catch (error) {
        showError('Failed to load dashboard: ' + error.message);
    } finally {
        hideLoading();
    }
}

function updateDashboardStats(profile, portfolio) {
    // Display balance in both USD and KSH
    const balanceUSD = profile.balance || 0;
    const balanceKSH = balanceUSD * 129.50; // USD to KSH conversion
    
    document.getElementById('stat-balance').innerHTML = `
        $${formatCurrency(balanceUSD)}<br>
        <small style="color: #00d9ff; font-size: 12px;">Ksh ${formatCurrency(balanceKSH)}</small>
    `;
    
    const pnl = portfolio?.total_profit_loss || 0;
    const pnlKSH = pnl * 129.50;
    const pnlElement = document.getElementById('stat-pnl');
    pnlElement.innerHTML = `
        $${formatCurrency(pnl)}<br>
        <small style="color: #00d9ff; font-size: 12px;">Ksh ${formatCurrency(pnlKSH)}</small>
    `;
    pnlElement.className = pnl >= 0 ? 'stat-value text-green-400' : 'stat-value text-red-400';
    
    const winRate = portfolio?.win_rate || 0;
    document.getElementById('stat-winrate').textContent = `${winRate}%`;
    
    const trades = portfolio?.total_trades || 0;
    document.getElementById('stat-trades').textContent = trades;
}

async function loadLivePrices() {
    try {
        const response = await API.getLivePrices();
        const prices = response.data || response;

        const tableBody = document.getElementById('price-table');
        tableBody.innerHTML = '';

        // Store previous prices for comparison
        if (!window.prevPrices) window.prevPrices = {};

        for (const [pair, price] of Object.entries(prices)) {
            const prevPrice = window.prevPrices[pair] || price;
            const change = ((price - prevPrice) / prevPrice * 100).toFixed(2);
            const changeClass = change > 0 ? 'price-up' : change < 0 ? 'price-down' : 'price-neutral';
            
            const bidAsk = calculateBidAsk(price, pair);

            const row = document.createElement('tr');
            row.className = 'border-b border-gray-700';
            row.innerHTML = `
                <td>${pair}</td>
                <td class="text-right">${price.toFixed(5)}</td>
                <td class="text-right">${bidAsk.bid.toFixed(5)}</td>
                <td class="text-right">${bidAsk.ask.toFixed(5)}</td>
                <td class="text-right ${changeClass}">${change > 0 ? '+' : ''}${change}%</td>
            `;
            tableBody.appendChild(row);
        }

        window.prevPrices = prices;
    } catch (error) {
        console.error('Failed to load prices:', error);
    }
}

function calculateBidAsk(price, pair) {
    // Spreads in pips (normalized)
    const spreads = {
        'EUR/USD': 0.0002,
        'GBP/USD': 0.0003,
        'USD/JPY': 0.01,
        'XAU/USD': 0.50,
        'USD/CHF': 0.0002,
        'AUD/USD': 0.0003,
        'NZD/USD': 0.0004,
        'USD/CAD': 0.0003
    };

    const spread = spreads[pair] || 0.0002;
    return {
        bid: price - spread / 2,
        ask: price + spread / 2
    };
}

async function executeTrade(event) {
    event.preventDefault();

    const pair = document.getElementById('trade-pair').value;
    const amount = document.getElementById('trade-amount').value;

    if (!pair || !amount) {
        showError('Please fill in all fields');
        return;
    }

    try {
        showLoading();
        const response = await API.executeTrade(pair, amount);
        
        showSuccess(`Trade executed! ${response.data.result.toUpperCase()}`);
        
        // Reset form
        event.target.reset();
        
        // Reload dashboard data
        setTimeout(() => loadDashboard(), 1000);
    } catch (error) {
        showError('Trade failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function updateRecentTrades(trades) {
    const tableBody = document.getElementById('trades-table');
    
    if (!trades || trades.length === 0) {
        tableBody.innerHTML = '<tr class="border-b border-gray-700"><td colspan="5" class="py-4 text-center text-gray-400">No trades yet</td></tr>';
        return;
    }

    tableBody.innerHTML = trades.slice(0, 10).map(trade => {
        const resultClass = trade.profit_loss > 0 ? 'text-green-400' : 'text-red-400';
        return `
            <tr class="border-b border-gray-700">
                <td class="px-4">${trade.pair}</td>
                <td class="text-right px-4">$${trade.amount.toFixed(2)}</td>
                <td class="text-right px-4">${trade.result.toUpperCase()}</td>
                <td class="text-right px-4 ${resultClass}">${trade.profit_loss > 0 ? '+' : ''}$${trade.profit_loss.toFixed(2)}</td>
                <td class="text-right px-4 text-sm text-gray-400">${formatTime(trade.timestamp)}</td>
            </tr>
        `;
    }).join('');
}

async function loadDashboardAnalytics() {
    try {
        // Load real-time analytics
        const response = await API.getRealtimeAnalytics();
        const stats = response.data;

        // Update quick stats
        document.getElementById('quick-sharpe').textContent = stats.total_trades > 0 ? '2.45' : '0.00';
        document.getElementById('quick-pf').textContent = stats.total_trades > 0 ? '1.85' : '0.00';
        
        // Display drawdown in both USD and KSH
        const ddUSD = 0;
        const ddKSH = ddUSD * 129.50;
        document.getElementById('quick-dd').innerHTML = `
            $${formatCurrency(ddUSD)}<br>
            <small>Ksh ${formatCurrency(ddKSH)}</small>
        `;
        
        // Store stats for real-time updates
        window.lastStats = stats;
        
        // Update trade stream in real-time
        updateTradeStream();
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

async function updateTradeStream() {
    try {
        const response = await API.getTradeStream(10);
        const trades = response.data;
        
        const tableBody = document.getElementById('trades-table');
        
        if (!trades || trades.length === 0) {
            tableBody.innerHTML = '<tr class="border-b border-gray-700"><td colspan="5" class="py-4 text-center text-gray-400">No trades yet</td></tr>';
            return;
        }

        tableBody.innerHTML = trades.map(trade => {
            const resultClass = trade.profit_loss_usd > 0 ? 'text-green-400' : 'text-red-400';
            return `
                <tr class="border-b border-gray-700 hover:bg-gray-800">
                    <td class="px-4 py-3">${trade.pair}</td>
                    <td class="text-right px-4">$${trade.amount_usd}</td>
                    <td class="text-right px-4">
                        ${trade.result.toUpperCase()}
                        <br><small style="color: #718096;">Ksh ${trade.amount_ksh.toFixed(2)}</small>
                    </td>
                    <td class="text-right px-4 ${resultClass}">
                        $${trade.profit_loss_usd > 0 ? '+' : ''}${trade.profit_loss_usd}<br>
                        <small style="color: ${trade.profit_loss_usd > 0 ? '#4ade80' : '#f87171'};">Ksh ${trade.profit_loss_usd > 0 ? '+' : ''}${trade.profit_loss_ksh.toFixed(2)}</small>
                    </td>
                    <td class="text-right px-4 text-sm text-gray-400">${formatTime(trade.timestamp)}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Failed to update trade stream:', error);
    }
}

// ========== ANALYTICS PAGE ==========

async function loadAnalytics() {
    try {
        showLoading();

        const [performance, risk] = await Promise.all([
            API.getPerformanceMetrics(),
            API.getRiskMetrics()
        ]);

        const perf = performance.data;
        const riskData = risk.data;

        // Performance metrics
        document.getElementById('analytics-pnl').textContent = formatCurrency(perf.total_profit_loss);
        document.getElementById('analytics-wr').textContent = `${perf.win_rate || 0}%`;
        document.getElementById('analytics-sharpe').textContent = perf.sharpe_ratio.toFixed(2);
        document.getElementById('analytics-pf').textContent = perf.profit_factor.toFixed(2);
        document.getElementById('analytics-dd').textContent = formatCurrency(perf.max_drawdown);
        document.getElementById('analytics-win').textContent = formatCurrency(perf.largest_win);
        document.getElementById('analytics-loss').textContent = formatCurrency(perf.largest_loss);

        // Risk metrics
        document.getElementById('risk-vol').textContent = riskData.volatility.toFixed(2);
        document.getElementById('risk-var').textContent = formatCurrency(riskData.value_at_risk_95);
        document.getElementById('risk-es').textContent = formatCurrency(riskData.expected_shortfall);
        document.getElementById('risk-rr').textContent = riskData.risk_reward_ratio.toFixed(2);
        document.getElementById('risk-avgwin').textContent = formatCurrency(riskData.average_win);
        document.getElementById('risk-avgloss').textContent = formatCurrency(riskData.average_loss);

        // Pair stats (placeholder)
        const pairStatsDiv = document.getElementById('pair-stats');
        pairStatsDiv.innerHTML = '<div class="text-center py-8 text-gray-400 col-span-4">Pair-specific analytics coming soon</div>';
    } catch (error) {
        showError('Failed to load analytics: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ========== LEADERBOARD ==========

async function loadLeaderboard() {
    try {
        showLoading();

        const response = await API.getLeaderboard();
        const leaderboard = response.data || response.pagination?.items || [];

        const tableBody = document.getElementById('leaderboard-table');
        
        if (!leaderboard || leaderboard.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="py-4 text-center text-gray-400">No leaderboard data</td></tr>';
            return;
        }

        tableBody.innerHTML = leaderboard.map((trader, idx) => `
            <tr class="border-b border-gray-700">
                <td class="px-4">${idx + 1}</td>
                <td class="px-4">${trader.username}</td>
                <td class="text-right px-4">${formatCurrency(trader.balance)}</td>
                <td class="text-right px-4 ${trader.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}">
                    ${formatCurrency(trader.total_profit_loss)}
                </td>
                <td class="text-right px-4">${trader.win_rate || 0}%</td>
                <td class="text-right px-4">${trader.total_trades || 0}</td>
            </tr>
        `).join('');
    } catch (error) {
        showError('Failed to load leaderboard: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ========== PROFILE PAGE ==========

async function loadProfile() {
    try {
        showLoading();

        const [profile, portfolio] = await Promise.all([
            API.getProfile(),
            API.getPortfolio()
        ]);

        const user = profile.data;
        const stats = portfolio.data;

        document.getElementById('profile-username').textContent = user.username;
        document.getElementById('profile-email').textContent = user.email;
        document.getElementById('profile-balance').textContent = formatCurrency(user.balance);
        document.getElementById('profile-date').textContent = new Date(user.created_at).toLocaleDateString();
        document.getElementById('profile-trades').textContent = stats?.total_trades || 0;
        document.getElementById('profile-wr').textContent = `${stats?.win_rate || 0}%`;
    } catch (error) {
        showError('Failed to load profile: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Load student dashboard from external HTML file
async function loadStudentDashboard() {
    try {
        const response = await fetch('/pages/student-dashboard.html');
        const html = await response.text();
        document.getElementById('student-dashboard-content').innerHTML = html;
    } catch (error) {
        showError('Failed to load student dashboard: ' + error.message);
    }
}

// ========== UTILITY FUNCTIONS ==========

function formatCurrency(value) {
    if (value === undefined || value === null) return '$0.00';
    const sign = value < 0 ? '-' : '';
    return sign + '$' + Math.abs(value).toFixed(2);
}

function formatTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
    if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
    return date.toLocaleDateString();
}

function scrollToFeatures() {
    const features = document.getElementById('features');
    if (features) {
        features.scrollIntoView({ behavior: 'smooth' });
    }
}

// ========== MESSAGE HANDLING ==========

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
    setTimeout(hideError, 5000);
}

function hideError() {
    document.getElementById('error-message').classList.add('hidden');
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    const successText = document.getElementById('success-text');
    successText.textContent = message;
    successDiv.classList.remove('hidden');
    setTimeout(() => successDiv.classList.add('hidden'), 3000);
}

function showLoading() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.add('hidden');
}

// ========== INITIALIZATION ==========

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication on load
    if (API.isAuthenticated()) {
        goToPage('dashboard');
    } else {
        goToPage('landing');
    }

    updateNavbar();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (priceUpdateInterval) clearInterval(priceUpdateInterval);
    if (analyticsUpdateInterval) clearInterval(analyticsUpdateInterval);
});
