import pytest
import json
from run import app
from db.database import users_db, accounts_db
from services import auth_service

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_test_data(app_context):
    # Clear databases
    users_db.clear()
    accounts_db.clear()
    
    # Create test user
    test_user = {
        'id': '123456',
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    users_db.append(test_user)
    
    # Create test account
    test_account = {
        'id': 'acc123',
        'user_id': '123456',
        'account_type': 'savings',
        'balance': 1000.0,
        'created_at': '2023-01-01T12:00:00'
    }
    accounts_db.append(test_account)
    
    # Generate token
    token = auth_service.generate_token(test_user['id'])
    
    return {
        'user': test_user,
        'account': test_account,
        'token': token
    }

def test_get_accounts(client, setup_test_data, app_context):
    # Test getting all accounts for a user
    response = client.get(
        '/accounts',
        headers={'Authorization': f"Bearer {setup_test_data['token']}"}
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'accounts' in data
    assert len(data['accounts']) == 1
    assert data['accounts'][0]['id'] == setup_test_data['account']['id']

def test_get_account_by_id(client, setup_test_data, app_context):
    # Test getting a specific account
    response = client.get(
        f"/accounts/{setup_test_data['account']['id']}",
        headers={'Authorization': f"Bearer {setup_test_data['token']}"}
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'account' in data
    assert data['account']['id'] == setup_test_data['account']['id']

def test_get_nonexistent_account(client, setup_test_data, app_context):
    # Test getting a non-existent account
    response = client.get(
        '/accounts/nonexistent',
        headers={'Authorization': f"Bearer {setup_test_data['token']}"}
    )
    
    assert response.status_code == 404

def test_create_account(client, setup_test_data, app_context):
    # Test creating a new account
    response = client.post(
        '/accounts',
        headers={
            'Authorization': f"Bearer {setup_test_data['token']}",
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'account_type': 'checking',
            'initial_balance': 500.0
        })
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'account' in data
    assert data['account']['account_type'] == 'checking'
    assert data['account']['balance'] == 500.0
    
    # Verify account was added to database
    assert len(accounts_db) == 2

def test_create_account_missing_fields(client, setup_test_data, app_context):
    # Test creating an account with missing fields
    response = client.post(
        '/accounts',
        headers={
            'Authorization': f"Bearer {setup_test_data['token']}",
            'Content-Type': 'application/json'
        },
        data=json.dumps({})
    )
    
    assert response.status_code == 400

def test_update_account(client, setup_test_data, app_context):
    # Test updating an account
    response = client.put(
        f"/accounts/{setup_test_data['account']['id']}",
        headers={
            'Authorization': f"Bearer {setup_test_data['token']}",
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'account_type': 'premium'
        })
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'account' in data
    assert data['account']['account_type'] == 'premium'

def test_delete_account(client, setup_test_data, app_context):
    # Test deleting an account
    response = client.delete(
        f"/accounts/{setup_test_data['account']['id']}",
        headers={'Authorization': f"Bearer {setup_test_data['token']}"}
    )
    
    assert response.status_code == 200
    
    # Verify account was removed from database
    assert len(accounts_db) == 0