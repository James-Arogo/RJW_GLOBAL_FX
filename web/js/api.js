/**
 * API Handler for RJW GLOBAL FX
 * Manages all backend API communication
 */

const API_BASE_URL = 'http://localhost:8000/api';
const API_TIMEOUT = 10000;

class APIHandler {
    constructor() {
        this.token = localStorage.getItem('token');
        this.refreshToken = localStorage.getItem('refreshToken');
        this.username = localStorage.getItem('username');
    }

    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.message || 'Request failed',
                    error_code: data.error_code,
                    details: data.details
                };
            }

            return data;
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    /**
     * Register new user
     */
    async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    /**
     * Login user
     */
    async login(username, password) {
        const response = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        // Store tokens
        this.token = response.data.access_token;
        this.refreshToken = response.data.refresh_token;
        this.username = username;

        localStorage.setItem('token', this.token);
        localStorage.setItem('refreshToken', this.refreshToken);
        localStorage.setItem('username', this.username);

        return response;
    }

    /**
     * Get user profile
     */
    async getProfile() {
        return this.request('/auth/profile', {
            method: 'GET'
        });
    }

    /**
     * Get live prices
     */
    async getLivePrices() {
        return this.request('/trade/live_prices', {
            method: 'GET'
        });
    }

    /**
     * Execute trade
     */
    async executeTrade(pair, amount) {
        return this.request('/trade/trade', {
            method: 'POST',
            body: JSON.stringify({ pair, amount: parseFloat(amount) })
        });
    }

    /**
     * Get trade history
     */
    async getTradeHistory() {
        return this.request(`/trade/history/${this.username}`, {
            method: 'GET'
        });
    }

    /**
     * Get portfolio stats
     */
    async getPortfolio() {
        return this.request(`/trade/portfolio/${this.username}`, {
            method: 'GET'
        });
    }

    /**
     * Get performance analytics
     */
    async getPerformanceMetrics() {
        return this.request('/analytics/user/performance', {
            method: 'GET'
        });
    }

    /**
     * Get risk metrics
     */
    async getRiskMetrics() {
        return this.request('/analytics/user/risk', {
            method: 'GET'
        });
    }

    /**
     * Get leaderboard
     */
    async getLeaderboard() {
        return this.request('/analytics/user/leaderboard', {
            method: 'GET'
        });
    }

    /**
     * Get real-time analytics
     */
    async getRealtimeAnalytics() {
        return this.request('/analytics/realtime', {
            method: 'GET'
        });
    }

    /**
     * Get pair analytics
     */
    async getPairAnalytics(pair) {
        return this.request(`/analytics/pair/${pair}`, {
            method: 'GET'
        });
    }

    /**
     * Get platform analytics
     */
    async getPlatformAnalytics() {
        return this.request('/analytics/platform', {
            method: 'GET'
        });
    }

    /**
     * Get live trade stream
     */
    async getTradeStream(limit = 20) {
        return this.request(`/analytics/stream?limit=${limit}`, {
            method: 'GET'
        });
    }

    /**
     * Refresh JWT token
     */
    async refreshJWT() {
        try {
            const response = await this.request('/auth/refresh', {
                method: 'POST',
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            this.token = response.data.access_token;
            localStorage.setItem('token', this.token);
            return response;
        } catch (error) {
            this.logout();
            throw error;
        }
    }

    /**
     * Logout
     */
    logout() {
        this.token = null;
        this.refreshToken = null;
        this.username = null;

        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('username');
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.token;
    }
}

// Global API instance
const API = new APIHandler();
