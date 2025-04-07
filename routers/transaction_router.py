from flask import Blueprint, request, jsonify
from services import transaction_service, auth_service, account_service

transaction_bp = Blueprint('transactions', __name__)


@transaction_bp.route('', methods=['GET'])
@auth_service.token_required
def get_transactions(current_user):
    # Get query parameters for filtering
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get user's accounts
    user_accounts = [account['id']
                     for account in account_service.get_user_accounts(current_user['id'])]

    # Get transactions
    user_transactions = transaction_service.get_user_transactions(
        user_accounts, account_id, start_date, end_date
    )

    return jsonify({'transactions': user_transactions}), 200


@transaction_bp.route('/<transaction_id>', methods=['GET'])
@auth_service.token_required
def get_transaction(current_user, transaction_id):
    # Get user's accounts
    user_accounts = [account['id']
                     for account in account_service.get_user_accounts(current_user['id'])]

    # Find the transaction
    transaction = transaction_service.get_transaction_by_id(transaction_id)

    if not transaction:
        return jsonify({'message': 'Transaction not found'}), 404

    # Check if user is authorized to view this transaction
    if transaction['source_account_id'] not in user_accounts and transaction['destination_account_id'] not in user_accounts:
        return jsonify({'message': 'Unauthorized to view this transaction'}), 403

    return jsonify({'transaction': transaction}), 200


@transaction_bp.route('', methods=['POST'])
@auth_service.token_required
def create_transaction(current_user):
    data = request.json

    if not data or not data.get('transaction_type') or not data.get('amount'):
        return jsonify({'message': 'Missing required fields'}), 400

    transaction_type = data.get('transaction_type')
    amount = float(data.get('amount'))

    if amount <= 0:
        return jsonify({'message': 'Amount must be positive'}), 400

    # Handle different transaction types
    if transaction_type == 'deposit':
        if not data.get('destination_account_id'):
            return jsonify({'message': 'Destination account ID is required for deposits'}), 400

        new_transaction, error = transaction_service.create_deposit(
            user_id=current_user['id'],
            destination_account_id=data.get('destination_account_id'),
            amount=amount
        )

    elif transaction_type == 'withdrawal':
        if not data.get('source_account_id'):
            return jsonify({'message': 'Source account ID is required for withdrawals'}), 400

        new_transaction, error = transaction_service.create_withdrawal(
            user_id=current_user['id'],
            source_account_id=data.get('source_account_id'),
            amount=amount
        )

    elif transaction_type == 'transfer':
        if not data.get('source_account_id') or not data.get('destination_account_id'):
            return jsonify({'message': 'Source and destination account IDs are required for transfers'}), 400

        new_transaction, error = transaction_service.create_transfer(
            user_id=current_user['id'],
            source_account_id=data.get('source_account_id'),
            destination_account_id=data.get('destination_account_id'),
            amount=amount
        )
    else:
        return jsonify({'message': 'Invalid transaction type'}), 400

    if error:
        return jsonify({'message': error}), 400 if 'Invalid' in error else 404

    return jsonify({'message': 'Transaction completed successfully', 'transaction': new_transaction}), 201
