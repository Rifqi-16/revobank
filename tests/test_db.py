import pytest
from db.database import users_db, accounts_db, transactions_db

@pytest.fixture
def setup_db():
    # Clear all database collections before each test
    users_db.clear()
    accounts_db.clear()
    transactions_db.clear()
    yield

def test_users_db(setup_db):
    # Test adding a user to the database
    test_user = {
        'id': '123456',
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    
    # Add user to database
    users_db.append(test_user)
    
    # Verify user was added
    assert len(users_db) == 1
    assert users_db[0]['id'] == '123456'
    assert users_db[0]['username'] == 'testuser'
    
    # Test updating a user
    users_db[0]['email'] = 'updated@example.com'
    assert users_db[0]['email'] == 'updated@example.com'
    
    # Test removing a user
    users_db.clear()
    assert len(users_db) == 0

def test_accounts_db(setup_db):
    # Test adding an account to the database
    test_account = {
        'id': 'acc123',
        'user_id': 'user123',
        'account_type': 'savings',
        'balance': 1000.0,
        'created_at': '2023-01-01T12:00:00'
    }
    
    # Add account to database
    accounts_db.append(test_account)
    
    # Verify account was added
    assert len(accounts_db) == 1
    assert accounts_db[0]['id'] == 'acc123'
    assert accounts_db[0]['balance'] == 1000.0
    
    # Test updating an account
    accounts_db[0]['balance'] = 1500.0
    assert accounts_db[0]['balance'] == 1500.0
    
    # Test removing an account
    accounts_db.clear()
    assert len(accounts_db) == 0

def test_transactions_db(setup_db):
    # Test adding a transaction to the database
    test_transaction = {
        'id': 'tx123',
        'transaction_type': 'transfer',
        'amount': 500.0,
        'source_account_id': 'acc1',
        'destination_account_id': 'acc2',
        'created_at': '2023-01-01T12:00:00'
    }
    
    # Add transaction to database
    transactions_db.append(test_transaction)
    
    # Verify transaction was added
    assert len(transactions_db) == 1
    assert transactions_db[0]['id'] == 'tx123'
    assert transactions_db[0]['amount'] == 500.0
    
    # Test updating a transaction
    transactions_db[0]['amount'] = 750.0
    assert transactions_db[0]['amount'] == 750.0
    
    # Test removing a transaction
    transactions_db.clear()
    assert len(transactions_db) == 0