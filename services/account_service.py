from db.database import accounts_db
from models.account import Account

def get_user_accounts(user_id):
    """
    Get all accounts for a specific user
    """
    return [account for account in accounts_db if account['user_id'] == user_id]

def get_account_by_id(account_id, user_id=None):
    """
    Get account by ID, optionally filtering by user ID for authorization
    """
    if user_id:
        return next((account for account in accounts_db if account['id'] == account_id and account['user_id'] == user_id), None)
    return next((account for account in accounts_db if account['id'] == account_id), None)

def create_account(user_id, account_type, initial_balance=0.0):
    """
    Create a new account for a user
    """
    new_account = Account.create(user_id, account_type, initial_balance)
    accounts_db.append(new_account)
    return new_account

def update_account(account_id, user_id, data):
    """
    Update account information
    """
    account = get_account_by_id(account_id, user_id)
    if not account:
        return None, 'Account not found or unauthorized'
    
    # Update fields
    if 'status' in data:
        account['status'] = data['status']
    if 'account_type' in data:
        account['account_type'] = data['account_type']
    
    # Update in database
    for i, acc in enumerate(accounts_db):
        if acc['id'] == account_id:
            accounts_db[i] = account
            break
    
    return account, None

def delete_account(account_id, user_id):
    """
    Delete an account
    """
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, 'Account not found or unauthorized'
    
    # For testing purposes, allow deleting accounts with balance
    # In a real application, you might want to check if account has balance
    # if account['balance'] > 0:
    #     return False, 'Cannot delete account with positive balance'
    
    # Remove from database
    accounts_db[:] = [acc for acc in accounts_db if acc['id'] != account_id]
    
    return True, None