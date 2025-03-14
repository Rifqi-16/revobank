from flask import Blueprint, request, jsonify
from services import user_service, auth_service

auth_router = Blueprint('auth', __name__)

@auth_router.route('/login', methods=['POST'])
def login():
    auth = request.json
    
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401
    
    user = user_service.get_user_by_username(auth.get('username'))
    
    if not user:
        return jsonify({'message': 'User not found'}), 401
    
    if user['password'] == auth.get('password'):  # In production, use proper password hashing
        token = auth_service.generate_token(user['id'])
        
        return jsonify({'token': token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401