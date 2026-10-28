import pytest
from utils.market_engine import MarketEngine
from utils.profit_manager import ProfitManager
from models import db, Trade, User


class TestMarketEngine:
    """Test MarketEngine utility."""
    
    def test_market_engine_initialization(self):
        """Test MarketEngine initialization."""
        engine = MarketEngine()
        
        assert isinstance(engine.prices, dict)
        assert 'EUR/USD' in engine.prices
        assert 'GBP/USD' in engine.prices
        assert 'USD/JPY' in engine.prices
        assert 'XAU/USD' in engine.prices
        assert engine.prices['EUR/USD'] == 1.10
    
    def test_get_prices(self):
        """Test getting live prices."""
        engine = MarketEngine()
        prices = engine.get_prices()
        
        assert isinstance(prices, dict)
        assert len(prices) == 4
        
        # Prices should be different after update (random change)
        initial_price = engine.prices['EUR/USD']
        engine.get_prices()
        assert engine.prices['EUR/USD'] != initial_price
    
    def test_execute_trade(self):
        """Test trade execution."""
        engine = MarketEngine()
        result = engine.execute_trade('EUR/USD', 100.0)
        
        assert isinstance(result, dict)
        assert result['pair'] == 'EUR/USD'
        assert 'result' in result
        assert 'profit_loss' in result
        assert 'timestamp' in result
        assert result['result'] in ['win', 'loss', 'neutral']
        assert isinstance(result['profit_loss'], (int, float))


class TestProfitManager:
    """Test ProfitManager utility."""
    
    def test_profit_manager_initialization(self):
        """Test ProfitManager initialization."""
        manager = ProfitManager()
        assert manager.min_profit_margin == 0.3
        
        custom_manager = ProfitManager(min_profit_margin=0.2)
        assert custom_manager.min_profit_margin == 0.2
    
    def test_enforce_margin(self):
        """Test profit margin enforcement."""
        manager = ProfitManager(0.3)
        
        # Test winning trade
        trade_result = {'profit_loss': 100.0}
        enforced = manager.enforce_margin(trade_result)
        
        assert enforced['profit_loss'] == 70.0  # 100 * (1 - 0.3)
        
        # Test losing trade
        trade_result = {'profit_loss': -100.0}
        enforced = manager.enforce_margin(trade_result)
        
        assert enforced['profit_loss'] == -70.0  # -100 * (1 - 0.3)
    
    def test_calculate_platform_profit(self, app, test_user):
        """Test platform profit calculation."""
        with app.app_context():
            # Create test trades
            trade1 = Trade(
                user_id=test_user.id,
                pair='EUR/USD',
                amount=100.0,
                result='win',
                profit_loss=100.0
            )
            trade2 = Trade(
                user_id=test_user.id,
                pair='GBP/USD',
                amount=50.0,
                result='loss',
                profit_loss=-50.0
            )
            
            db.session.add(trade1)
            db.session.add(trade2)
            db.session.commit()
            
            manager = ProfitManager(0.3)
            platform_profit = manager.calculate_platform_profit()
            
            # Total profit: 100 - 50 = 50
            # Platform profit: 50 * 0.3 = 15
            assert platform_profit == 15.0
