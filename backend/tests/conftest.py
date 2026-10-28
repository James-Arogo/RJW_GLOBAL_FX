import pytest
import tempfile
import os
from app import create_app
from models import db, User, Trade, AdminAudit
from config import TestingConfig


@pytest.fixture
def app():
    """Create and configure a test app."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            password='hashed_password',
            balance=1000.0
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
