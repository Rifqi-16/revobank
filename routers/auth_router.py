from flask import Blueprint, request, jsonify
from services import user_service, auth_service

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = user_service.get_user_by_username(auth.get('username'))

    if not user:
        return jsonify({'message': 'User not found'}), 401

    # In production, use proper password hashing
    if user.password_hash == auth.get('password'):
        token = auth_service.generate_token(user.id)

        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401
