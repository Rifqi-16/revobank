from flask import Flask, jsonify
from flask_migrate import Migrate
from db.database import db
import os
import datetime


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'revobank_secret_key')
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    # Prioritize DATABASE_URL environment variable for deployment
    # Only fallback to localhost in development environment
    if not database_url:
        app.logger.warning(
            "DATABASE_URL not found in environment variables, using default local database")
        database_url = 'postgresql://postgres:postgres@localhost:5432/revobank'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Configure database connection options based on environment
    # For deployment environments, we need more resilient settings
    engine_options = {
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_size': 5,
        'max_overflow': 10
    }

    # Only add connect_args for non-Supabase connections
    # Supabase and some managed PostgreSQL services don't support all these parameters
    if database_url and 'supabase.com' not in database_url:
        engine_options['connect_args'] = {
            'connect_timeout': 30,
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5
        }

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options

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
        # Check database connection status
        db_status = "connected"
        db_error = None
        try:
            with db.engine.connect() as connection:
                pass
        except Exception as e:
            db_status = "disconnected"
            db_error = str(e)
            app.logger.error(
                f"Database connection error on index route: {str(e)}")

        return jsonify({
            'name': 'RevoBank API',
            'version': '1.0',
            'description': 'A RESTful API for banking operations',
            'status': db_status,
            'database_info': {
                'connection_status': db_status,
                'error': db_error,
                'host': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] and len(app.config['SQLALCHEMY_DATABASE_URI'].split('@')) > 1 else 'unknown'
            },
            'environment': os.getenv('ENVIRONMENT', 'development'),
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
            'status': 'active',
            'deployment_info': {
                'is_koyeb': os.getenv('KOYEB') == 'true',
                'environment': os.getenv('ENVIRONMENT', 'development')
            }
        })

    # Register blueprints
    app.register_blueprint(auth_router, url_prefix='/login')
    app.register_blueprint(user_router, url_prefix='/users')
    app.register_blueprint(account_router, url_prefix='/accounts')
    app.register_blueprint(transaction_router, url_prefix='/transactions')

    # Add diagnostic endpoint for troubleshooting
    @app.route('/diagnostics')
    def diagnostics():
        # Check database connection
        db_status = "connected"
        db_error = None
        connection_time = None
        try:
            start_time = datetime.datetime.now()
            with db.engine.connect() as connection:
                connection_time = (datetime.datetime.now() -
                                   start_time).total_seconds()
        except Exception as e:
            db_status = "disconnected"
            db_error = str(e)
            app.logger.error(
                f"Database connection error on diagnostics route: {str(e)}")

        # Get database URL info (safely)
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        db_host = "unknown"
        db_type = "unknown"

        try:
            if '@' in db_url and len(db_url.split('@')) > 1:
                db_host = db_url.split('@')[1].split('/')[0]

            if '://' in db_url:
                db_type = db_url.split('://')[0]
        except Exception as e:
            app.logger.error(f"Error parsing database URL: {str(e)}")

        return jsonify({
            'timestamp': datetime.datetime.now().isoformat(),
            'application': {
                'name': 'RevoBank API',
                'version': '1.0',
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'is_koyeb': os.getenv('KOYEB') == 'true'
            },
            'database': {
                'connection_status': db_status,
                'connection_time_seconds': connection_time,
                'error': db_error,
                'type': db_type,
                'host': db_host,
                'database_url_set': os.getenv('DATABASE_URL') is not None
            },
            'environment_variables': {
                'KOYEB': os.getenv('KOYEB') is not None,
                'ENVIRONMENT': os.getenv('ENVIRONMENT') is not None,
                'DATABASE_URL': os.getenv('DATABASE_URL') is not None,
                'SECRET_KEY': os.getenv('SECRET_KEY') is not None
            }
        })

    # Add sample data for testing
    from werkzeug.security import generate_password_hash

    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                # Test database connection
                app.logger.info("Attempting to connect to database at: %s",
                                app.config['SQLALCHEMY_DATABASE_URI'].replace(":postgres@", ":****@"))
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
