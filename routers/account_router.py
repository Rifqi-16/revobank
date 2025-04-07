from flask import Blueprint, request, jsonify
from services import account_service, auth_service

account_bp = Blueprint('accounts', __name__)


@account_bp.route('', methods=['GET'])
@auth_service.token_required
def get_accounts(current_user):
    user_accounts = account_service.get_user_accounts(current_user['id'])
    return jsonify({'accounts': user_accounts}), 200


@account_bp.route('/<account_id>', methods=['GET'])
@auth_service.token_required
def get_account(current_user, account_id):
    account = account_service.get_account_by_id(account_id, current_user['id'])

    if not account:
        return jsonify({'message': 'Account not found or unauthorized'}), 404

    return jsonify({'account': account}), 200


@account_bp.route('', methods=['POST'])
@auth_service.token_required
def create_account(current_user):
    data = request.json

    if not data or not data.get('account_type'):
        return jsonify({'message': 'Missing required fields'}), 400

    new_account = account_service.create_account(
        user_id=current_user['id'],
        account_type=data.get('account_type'),
        initial_balance=data.get('initial_balance', 0.0)
    )

    return jsonify({'message': 'Account created successfully', 'account': new_account}), 201


@account_bp.route('/<account_id>', methods=['PUT'])
@auth_service.token_required
def update_account(current_user, account_id):
    data = request.json

    updated_account, error = account_service.update_account(
        account_id, current_user['id'], data)

    if error:
        return jsonify({'message': error}), 404

    return jsonify({'message': 'Account updated successfully', 'account': updated_account}), 200


@account_bp.route('/<account_id>', methods=['DELETE'])
@auth_service.token_required
def delete_account(current_user, account_id):
    success, error = account_service.delete_account(
        account_id, current_user['id'])

    if not success:
        # Check if error is None before using 'in' operator
        return jsonify({'message': error or 'Unknown error'}), 400 if error and 'balance' in error else 404

    return jsonify({'message': 'Account deleted successfully'}), 200
