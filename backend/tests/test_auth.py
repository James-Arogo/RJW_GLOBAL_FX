import pytest
from werkzeug.security import generate_password_hash
from models import db, User


class TestAuthRoutes:
    """Test authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Registration successful'
        
        # Verify user was created in database
        with client.application.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.username == 'newuser'
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Username already exists'
    
    def test_register_missing_data(self, client):
        """Test registration with missing required data."""
        response = client.post('/api/auth/register', json={
            'username': 'incomplete'
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful user login."""
        # Update test user with hashed password
        with client.application.app_context():
            test_user.password = generate_password_hash('testpass')
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert data['username'] == 'testuser'
        assert 'balance' in data
        assert 'access_token' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'Invalid credentials'
    
    def test_login_missing_data(self, client):
        """Test login with missing required data."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
