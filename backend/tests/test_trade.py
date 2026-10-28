import pytest
from models import db, Trade


class TestTradeRoutes:
    """Test trading routes."""
    
    def test_get_live_prices(self, client):
        """Test getting live market prices."""
        response = client.get('/api/trade/live_prices')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'EUR/USD' in data
        assert 'GBP/USD' in data
        assert 'USD/JPY' in data
        assert 'XAU/USD' in data
    
    def test_execute_trade_success(self, client, test_user):
        """Test successful trade execution."""
        response = client.post('/api/trade/trade', json={
            'username': 'testuser',
            'pair': 'EUR/USD',
            'amount': 100.0
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['pair'] == 'EUR/USD'
        assert data['amount'] == 100.0
        assert 'result' in data
        assert 'profit_loss' in data
        assert 'balance' in data
        assert data['result'] in ['win', 'loss', 'neutral']
    
    def test_execute_trade_user_not_found(self, client):
        """Test trade execution with non-existent user."""
        response = client.post('/api/trade/trade', json={
            'username': 'nonexistent',
            'pair': 'EUR/USD',
            'amount': 100.0
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'User not found'
    
    def test_execute_trade_insufficient_balance(self, client, test_user):
        """Test trade execution with insufficient balance."""
        # Set user balance to very low amount
        with client.application.app_context():
            test_user.balance = 10.0
            db.session.commit()
        
        response = client.post('/api/trade/trade', json={
            'username': 'testuser',
            'pair': 'EUR/USD',
            'amount': 1000.0
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Insufficient balance' in data['message']
    
    def test_execute_trade_invalid_pair(self, client, test_user):
        """Test trade execution with invalid currency pair."""
        response = client.post('/api/trade/trade', json={
            'username': 'testuser',
            'pair': 'INVALID/PAIR',
            'amount': 100.0
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid currency pair' in data['message']
    
    def test_trade_history(self, client, test_user):
        """Test getting user trade history."""
        # Create some test trades
        with client.application.app_context():
            trade1 = Trade(
                user_id=test_user.id,
                pair='EUR/USD',
                amount=100.0,
                result='win',
                profit_loss=10.0
            )
            trade2 = Trade(
                user_id=test_user.id,
                pair='GBP/USD',
                amount=50.0,
                result='loss',
                profit_loss=-5.0
            )
            db.session.add(trade1)
            db.session.add(trade2)
            db.session.commit()
        
        response = client.get(f'/api/trade/history/{test_user.username}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['pair'] == 'EUR/USD'
        assert data[1]['pair'] == 'GBP/USD'
