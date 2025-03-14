import pytest
import jwt
from flask import current_app
from services import auth_service
from db.database import users_db

@pytest.fixture
def setup_user():
    # Create a test user
    test_user = {
        'id': '123456',
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }
    
    # Clear users and add test user
    users_db.clear()
    users_db.append(test_user)
    
    return test_user

def test_generate_token(setup_user, app_context):
    # Test token generation
    token = auth_service.generate_token(setup_user['id'])
    
    # Verify token is a string
    assert isinstance(token, str)
    
    # Decode token and verify payload
    decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    assert decoded['user_id'] == setup_user['id']
    assert 'exp' in decoded

@pytest.fixture
def test_client(app_context):
    from run import app
    return app.test_client()

@pytest.fixture
def protected_route(app_context):
    from flask import Blueprint
    bp = Blueprint('test', __name__)
    
    @bp.route('/protected')
    @auth_service.token_required
    def protected(current_user):
        return {'success': True, 'user_id': current_user['id']}
    
    from run import app
    app.register_blueprint(bp)
    return '/protected'

def test_token_required_missing_token(test_client, setup_user, protected_route):
    # Make request without token
    response = test_client.get(protected_route)
    
    # Verify response
    assert response.status_code == 401
    assert response.json['message'] == 'Token is missing!'

def test_token_required_valid_token(test_client, setup_user, protected_route):
    # Generate a valid token
    token = auth_service.generate_token(setup_user['id'])
    
    # Make request with valid token
    response = test_client.get(
        protected_route,
        headers={'Authorization': f'Bearer {token}'}
    )
    
    # Verify response
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['user_id'] == setup_user['id']

def test_token_required_invalid_token(test_client, setup_user, protected_route):
    # Make request with invalid token
    response = test_client.get(
        protected_route,
        headers={'Authorization': 'Bearer invalid_token'}
    )
    
    # Verify response
    assert response.status_code == 401
    assert response.json['message'] == 'Token is invalid!'