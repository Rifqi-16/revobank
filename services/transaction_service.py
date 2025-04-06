from datetime import datetime
from db.database import db
from models.account import Account
from models.transaction import Transaction


def get_user_transactions(user_accounts, account_id=None, start_date=None, end_date=None):
    """
    Get transactions for a user's accounts with optional filtering
    """
    query = Transaction.query.filter(
        (Transaction.from_account_id.in_(user_accounts)) |
        (Transaction.to_account_id.in_(user_accounts))
    )

    if account_id:
        query = query.filter(
            (Transaction.from_account_id == account_id) |
            (Transaction.to_account_id == account_id)
        )

    if start_date:
        query = query.filter(Transaction.created_at >=
                             datetime.fromisoformat(start_date))

    if end_date:
        query = query.filter(Transaction.created_at <=
                             datetime.fromisoformat(end_date))

    return query.all()


def get_transaction_by_id(transaction_id):
    """
    Get a transaction by ID
    """
    return Transaction.query.get(transaction_id)


def create_deposit(user_id, destination_account_id, amount):
    """
    Process a deposit transaction
    """
    destination_account = Account.query.filter_by(
        id=destination_account_id,
        user_id=user_id
    ).first()

    if not destination_account:
        return None, 'Invalid account'

    try:
        # Process deposit
        destination_account.balance += amount

        # Create transaction record
        new_transaction = Transaction(
            type='deposit',
            amount=amount,
            to_account_id=destination_account.id,
            created_at=datetime.utcnow()
        )

        db.session.add(new_transaction)
        db.session.commit()

        return new_transaction, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def create_withdrawal(user_id, source_account_id, amount):
    """
    Process a withdrawal transaction
    """
    source_account = Account.query.filter_by(
        id=source_account_id,
        user_id=user_id
    ).first()

    if not source_account:
        return None, 'Invalid account'

    if source_account.balance < amount:
        return None, 'Insufficient balance'

    try:
        # Process withdrawal
        source_account.balance -= amount

        # Create transaction record
        new_transaction = Transaction(
            type='withdrawal',
            amount=amount,
            from_account_id=source_account.id,
            created_at=datetime.utcnow()
        )

        db.session.add(new_transaction)
        db.session.commit()

        return new_transaction, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def create_transfer(user_id, source_account_id, destination_account_id, amount):
    """
    Process a transfer transaction
    """
    source_account = Account.query.filter_by(
        id=source_account_id,
        user_id=user_id
    ).first()

    if not source_account:
        return None, 'Invalid source account'

    destination_account = Account.query.get(destination_account_id)

    if not destination_account:
        return None, 'Invalid destination account'

    if source_account.balance < amount:
        return None, 'Insufficient balance'

    try:
        # Process transfer
        source_account.balance -= amount
        destination_account.balance += amount

        # Create transaction record
        new_transaction = Transaction(
            type='transfer',
            amount=amount,
            from_account_id=source_account.id,
            to_account_id=destination_account.id,
            created_at=datetime.utcnow()
        )

        db.session.add(new_transaction)
        db.session.commit()

        return new_transaction, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
