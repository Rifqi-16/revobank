import pytest
import json
from run import app
from db.database import users_db

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_test_user():
    # Clear users database
    users_db.clear()
    
    # Create test user
    test_user = {
        'id': '123456',
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    users_db.append(test_user)
    
    return test_user

def test_login_success(client, setup_test_user, app_context):
    # Test successful login
    response = client.post(
        '/login/login',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'username': 'testuser',
            'password': 'password123'
        })
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'token' in data
    assert isinstance(data['token'], str)

def test_login_invalid_credentials(client, setup_test_user, app_context):
    # Test login with invalid password
    response = client.post(
        '/login/login',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        })
    )
    
    assert response.status_code == 401

def test_login_user_not_found(client, setup_test_user, app_context):
    # Test login with non-existent user
    response = client.post(
        '/login/login',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            'username': 'nonexistentuser',
            'password': 'password123'
        })
    )
    
    assert response.status_code == 401

def test_login_missing_fields(client, setup_test_user, app_context):
    # Test login with missing fields
    response = client.post(
        '/login/login',
        headers={'Content-Type': 'application/json'},
        data=json.dumps({})
    )
    
    assert response.status_code == 401