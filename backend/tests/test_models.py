import pytest
from datetime import datetime
from models import db, User, Trade, AdminAudit


class TestModels:
    """Test database models."""
    
    def test_user_model_creation(self, app):
        """Test User model creation and relationships."""
        with app.app_context():
            user = User(
                username='modeltest',
                password='hashed_password',
                balance=1500.0
            )
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            assert user.id is not None
            assert user.username == 'modeltest'
            assert user.balance == 1500.0
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)
    
    def test_user_model_unique_username(self, app):
        """Test that username must be unique."""
        with app.app_context():
            user1 = User(username='duplicate', password='pass1')
            user2 = User(username='duplicate', password='pass2')
            
            db.session.add(user1)
            db.session.commit()
            
            db.session.add(user2)
            with pytest.raises(Exception):  # Should raise IntegrityError
                db.session.commit()
    
    def test_trade_model_creation(self, app, test_user):
        """Test Trade model creation and relationships."""
        with app.app_context():
            trade = Trade(
                user_id=test_user.id,
                pair='EUR/USD',
                amount=100.0,
                result='win',
                profit_loss=15.50
            )
            db.session.add(trade)
            db.session.commit()
            
            # Verify trade was created
            assert trade.id is not None
            assert trade.user_id == test_user.id
            assert trade.pair == 'EUR/USD'
            assert trade.amount == 100.0
            assert trade.result == 'win'
            assert trade.profit_loss == 15.50
            assert trade.timestamp is not None
            assert isinstance(trade.timestamp, datetime)
            
            # Test relationship
            assert trade.user.username == 'testuser'
    
    def test_admin_audit_model_creation(self, app):
        """Test AdminAudit model creation."""
        with app.app_context():
            audit = AdminAudit(
                action='User registration: testuser'
            )
            db.session.add(audit)
            db.session.commit()
            
            # Verify audit was created
            assert audit.id is not None
            assert audit.action == 'User registration: testuser'
            assert audit.timestamp is not None
            assert isinstance(audit.timestamp, datetime)
    
    def test_user_trade_relationship(self, app, test_user):
        """Test one-to-many relationship between User and Trade."""
        with app.app_context():
            # Create multiple trades for the user
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
            
            # Test relationship
            assert len(test_user.trades) == 2
            assert test_user.trades[0].pair == 'EUR/USD'
            assert test_user.trades[1].pair == 'GBP/USD'
