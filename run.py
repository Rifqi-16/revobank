from flask import Flask, jsonify
from flask_migrate import Migrate
from db.database import db
import os


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'revobank_secret_key')
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'postgresql://postgres:postgres@localhost:5432/revobank'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 30,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }
    }

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Import models and routers after db initialization
    from models.user import User
    from models.account import Account
    from models.transaction import Transaction
    from routers.auth_router import auth_router
    from routers.user_router import user_router
    from routers.account_router import account_router
    from routers.transaction_router import transaction_router

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
    from werkzeug.security import generate_password_hash

    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                # Test database connection
                db.engine.connect()
                app.logger.info("Successfully connected to the database")
                # Initialize database tables
                db.create_all()
                app.logger.info("Database tables created successfully")

                # Add sample user if not exists
                if not User.query.filter_by(username='demo').first():
                    app.logger.info("Creating sample user...")
                    sample_user = User(
                        username='demo',
                        password_hash=generate_password_hash('password'),
                        email='demo@revobank.com',
                        full_name='Demo User'
                    )
                    db.session.add(sample_user)
                    db.session.commit()
                    app.logger.info("Sample user created successfully")

                    # Add sample account
                    app.logger.info("Creating sample account...")
                    sample_account = Account(
                        user_id=sample_user.id,
                        account_type='savings',
                        account_number='1234567890',
                        balance=1000.0
                    )
                    db.session.add(sample_account)
                    db.session.commit()
                    app.logger.info("Sample account created successfully")
                else:
                    app.logger.info(
                        "Sample user already exists, skipping sample data creation")

            except Exception as e:
                retries -= 1
                if retries == 0:
                    app.logger.error(
                        f"Failed to connect to database after 5 attempts: {str(e)}")
                    raise
                app.logger.warning(
                    f"Database connection attempt failed. Retrying in 5 seconds... ({retries} attempts left)")
                import time
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                app.logger.info(
                    "Database connection and initialization completed successfully")
                break  # Break the loop if connection is successful

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
