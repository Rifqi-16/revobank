import pytest
from services import account_service
from db.database import accounts_db, users_db
import uuid

@pytest.fixture
def setup_accounts():
    # Clear the accounts database before each test
    accounts_db.clear()
    yield

@pytest.fixture
def setup_user():
    # Create a test user
    user_id = str(uuid.uuid4())
    test_user = {
        'id': user_id,
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    
    # Clear users and add test user
    users_db.clear()
    users_db.append(test_user)
    
    return test_user

def test_create_account(setup_accounts, setup_user):
    # Test creating a new account
    account = account_service.create_account(
        user_id=setup_user['id'],
        account_type='savings',
        initial_balance=1000.0
    )
    
    assert account is not None
    assert account['user_id'] == setup_user['id']
    assert account['account_type'] == 'savings'
    assert account['balance'] == 1000.0
    assert 'id' in account
    assert 'created_at' in account
    
    # Verify account was added to the database
    assert len(accounts_db) == 1
    assert accounts_db[0]['user_id'] == setup_user['id']

def test_get_account_by_id(setup_accounts, setup_user):
    # Create an account
    created_account = account_service.create_account(
        user_id=setup_user['id'],
        account_type='checking',
        initial_balance=500.0
    )
    
    # Get account by ID
    account = account_service.get_account_by_id(created_account['id'])
    
    assert account is not None
    assert account['id'] == created_account['id']
    assert account['account_type'] == 'checking'
    
    # Test non-existent account
    non_existent = account_service.get_account_by_id('nonexistent-id')
    assert non_existent is None

def test_get_user_accounts(setup_accounts, setup_user):
    # Create multiple accounts for the user
    account_service.create_account(
        user_id=setup_user['id'],
        account_type='savings',
        initial_balance=1000.0
    )
    
    account_service.create_account(
        user_id=setup_user['id'],
        account_type='checking',
        initial_balance=500.0
    )
    
    # Get all accounts for the user
    user_accounts = account_service.get_user_accounts(setup_user['id'])
    
    assert len(user_accounts) == 2
    assert all(account['user_id'] == setup_user['id'] for account in user_accounts)
    
    # Test user with no accounts
    other_user_id = str(uuid.uuid4())
    no_accounts = account_service.get_user_accounts(other_user_id)
    assert len(no_accounts) == 0