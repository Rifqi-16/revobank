from flask import Flask, jsonify
from routers.auth_router import auth_router
from routers.user_router import user_router
from routers.account_router import account_router
from routers.transaction_router import transaction_router
from services import account_service

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'revobank_secret_key'
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'name': 'RevoBank API',
            'version': '1.0',
            'description': 'A RESTful API for banking operations',
            'endpoints': {
                'auth': {
                    'path': '/login',
                    'methods': ['POST'],
                    'description': 'User authentication endpoint for login'
                },
                'users': {
                    'path': '/users',
                    'methods': ['GET', 'POST'],
                    'description': 'User management - create and retrieve user information'
                },
                'accounts': {
                    'path': '/accounts',
                    'methods': ['GET', 'POST'],
                    'description': 'Bank account operations - create and manage accounts'
                },
                'transactions': {
                    'path': '/transactions',
                    'methods': ['GET', 'POST'],
                    'description': 'Transaction operations - create and view transactions'
                }
            },
            'documentation': 'Refer to API_README.md for detailed documentation',
            'status': 'active'
        })
    
    # Register blueprints
    app.register_blueprint(auth_router, url_prefix='/login')
    app.register_blueprint(user_router, url_prefix='/users')
    app.register_blueprint(account_router, url_prefix='/accounts')
    app.register_blueprint(transaction_router, url_prefix='/transactions')
    
    # Add sample data for testing
    from db.database import users_db, accounts_db
    import uuid
    import datetime
    
    # Add sample user
    if not any(user['username'] == 'demo' for user in users_db):
        sample_user = {
            'id': str(uuid.uuid4()),
            'username': 'demo',
            'password': 'password',  # In production, hash the password
            'email': 'demo@revobank.com',
            'full_name': 'Demo User',
            'created_at': datetime.datetime.now().isoformat()
        }
        users_db.append(sample_user)
        
        # Add sample account
        sample_account = account_service.create_account(
            user_id=sample_user['id'],
            account_type='savings',
            initial_balance=1000.0
        )
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)