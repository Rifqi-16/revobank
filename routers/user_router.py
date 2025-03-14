from flask import Blueprint, request, jsonify
from services import user_service, auth_service
from models.user import User

user_router = Blueprint('users', __name__)

@user_router.route('', methods=['POST'])
def create_user():
    data = request.json
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    new_user, error = user_service.create_user(
        username=data.get('username'),
        password=data.get('password'),
        email=data.get('email'),
        full_name=data.get('full_name', '')
    )
    
    if error:
        return jsonify({'message': error}), 409
    
    return jsonify({
        'message': 'User created successfully',
        'user': User.to_response(new_user)
    }), 201

@user_router.route('/me', methods=['GET'])
@auth_service.token_required
def get_user_profile(current_user):
    return jsonify({'user': User.to_response(current_user)}), 200

@user_router.route('/me', methods=['PUT'])
@auth_service.token_required
def update_user_profile(current_user):
    data = request.json
    
    updated_user, error = user_service.update_user(current_user['id'], data)
    
    if error:
        return jsonify({'message': error}), 400
    
    return jsonify({
        'message': 'Profile updated successfully', 
        'user': User.to_response(updated_user)
    }), 200