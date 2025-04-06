from db.database import db
from models.account import Account


def get_user_accounts(user_id):
    """
    Get all accounts for a specific user
    """
    return Account.query.filter_by(user_id=user_id).all()


def get_account_by_id(account_id, user_id=None):
    """
    Get account by ID, optionally filtering by user ID for authorization
    """
    query = Account.query.filter_by(id=account_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    return query.first()


def create_account(user_id, account_type, initial_balance=0.0):
    """
    Create a new account for a user
    """
    new_account = Account(
        user_id=user_id,
        account_type=account_type,
        balance=initial_balance
    )
    db.session.add(new_account)
    db.session.commit()
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
        account.status = data['status']
    if 'account_type' in data:
        account.account_type = data['account_type']

    try:
        db.session.commit()
        return account, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_account(account_id, user_id):
    """
    Delete an account
    """
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, 'Account not found or unauthorized'

    try:
        db.session.delete(account)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)
