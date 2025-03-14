import datetime
from db.database import accounts_db, transactions_db
from models.transaction import Transaction

def get_user_transactions(user_accounts, account_id=None, start_date=None, end_date=None):
    """
    Get transactions for a user's accounts with optional filtering
    """
    user_transactions = []
    for transaction in transactions_db:
        if transaction['source_account_id'] in user_accounts or transaction['destination_account_id'] in user_accounts:
            # Apply account filter if provided
            if account_id and transaction['source_account_id'] != account_id and transaction['destination_account_id'] != account_id:
                continue
            
            # Apply date filters if provided
            transaction_date = datetime.datetime.fromisoformat(transaction['created_at'])
            
            if start_date:
                start = datetime.datetime.fromisoformat(start_date)
                if transaction_date < start:
                    continue
            
            if end_date:
                end = datetime.datetime.fromisoformat(end_date)
                if transaction_date > end:
                    continue
            
            user_transactions.append(transaction)
    
    return user_transactions

def get_transaction_by_id(transaction_id):
    """
    Get a transaction by ID
    """
    return next((t for t in transactions_db if t['id'] == transaction_id), None)

def create_deposit(user_id, destination_account_id, amount):
    """
    Process a deposit transaction
    """
    # Verify account exists and belongs to user
    destination_account = next((account for account in accounts_db 
                               if account['id'] == destination_account_id 
                               and account['user_id'] == user_id), None)
    
    if not destination_account:
        return None, 'Invalid account'
    
    # Process deposit
    for i, account in enumerate(accounts_db):
        if account['id'] == destination_account['id']:
            accounts_db[i]['balance'] += amount
            destination_account = accounts_db[i]
            break
    
    # Create transaction record
    new_transaction = Transaction.create('deposit', amount, None, destination_account['id'])
    transactions_db.append(new_transaction)
    
    return new_transaction, None

def create_withdrawal(user_id, source_account_id, amount):
    """
    Process a withdrawal transaction
    """
    # Verify account exists and belongs to user
    source_account = next((account for account in accounts_db 
                          if account['id'] == source_account_id 
                          and account['user_id'] == user_id), None)
    
    if not source_account:
        return None, 'Invalid account'
    
    # Verify sufficient balance
    if source_account['balance'] < amount:
        return None, 'Insufficient balance'
    
    # Process withdrawal
    for i, account in enumerate(accounts_db):
        if account['id'] == source_account['id']:
            accounts_db[i]['balance'] -= amount
            source_account = accounts_db[i]
            break
    
    # Create transaction record
    new_transaction = Transaction.create('withdrawal', amount, source_account['id'], None)
    transactions_db.append(new_transaction)
    
    return new_transaction, None

def create_transfer(user_id, source_account_id, destination_account_id, amount):
    """
    Process a transfer transaction
    """
    # Verify source account exists and belongs to user
    source_account = next((account for account in accounts_db 
                          if account['id'] == source_account_id 
                          and account['user_id'] == user_id), None)
    
    if not source_account:
        return None, 'Invalid source account'
    
    # Verify destination account exists
    destination_account = next((account for account in accounts_db 
                               if account['id'] == destination_account_id), None)
    
    if not destination_account:
        return None, 'Invalid destination account'
    
    # Verify sufficient balance
    if source_account['balance'] < amount:
        return None, 'Insufficient balance'
    
    # Process transfer
    for i, account in enumerate(accounts_db):
        if account['id'] == source_account['id']:
            accounts_db[i]['balance'] -= amount
            source_account = accounts_db[i]
        elif account['id'] == destination_account['id']:
            accounts_db[i]['balance'] += amount
            destination_account = accounts_db[i]
    
    # Create transaction record
    new_transaction = Transaction.create('transfer', amount, source_account['id'], destination_account['id'])
    transactions_db.append(new_transaction)
    
    return new_transaction, None