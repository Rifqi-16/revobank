from flask import Flask, jsonify
from flask_migrate import Migrate
from db.database import db
import os
import datetime


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'revobank_secret_key')
    database_url = os.getenv('DATABASE_URL')

    # Ensure we're using the correct protocol for PostgreSQL
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.logger.info("Converted postgres:// URL to postgresql:// format")

    # Log the database URL (with password masked)
    if database_url:
        masked_url = database_url
        if '@' in masked_url:
            parts = masked_url.split('@')
            auth_parts = parts[0].split(':')
            if len(auth_parts) > 1:  # Fixed condition to properly mask password
                masked_url = f"{auth_parts[0]}:****@{parts[1]}"
        app.logger.info(f"Using database URL: {masked_url}")

        # Additional logging for Koyeb environment
        if os.getenv('KOYEB') == 'true':
            app.logger.info(
                "Running in Koyeb environment with provided DATABASE_URL")
    else:
        app.logger.warning(
            "DATABASE_URL not found in environment variables, using default local database")
        database_url = 'postgresql://postgres:postgres@localhost:5432/revobank'
        app.logger.info("Using default local database connection string")

    # Check if we're running in Koyeb environment
    is_koyeb = os.getenv('KOYEB') == 'true'
    is_production = os.getenv('ENVIRONMENT') == 'production'

    # Log environment detection
    app.logger.info(
        f"Environment detection: Koyeb={is_koyeb}, Production={is_production}")

    # Define SQLite fallback path first so it can be used in all conditions
    sqlite_fallback_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'revobank.db')

    # Force enable SQLite fallback in Koyeb environment for resilience
    if is_koyeb:
        use_sqlite_fallback = True
        app.logger.info("SQLite fallback enabled for Koyeb deployment")

        # Ensure we're not using localhost in Koyeb environment
        if not database_url or 'localhost' in database_url:
            app.logger.warning(
                "Invalid database configuration detected in Koyeb environment")
            # Try to get DATABASE_URL directly from environment again
            koyeb_db_url = os.getenv('DATABASE_URL')
            if koyeb_db_url and 'localhost' not in koyeb_db_url:
                app.logger.info(
                    "Using DATABASE_URL from environment variables")
                database_url = koyeb_db_url
                # Ensure we're using the correct protocol for PostgreSQL
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace(
                        'postgres://', 'postgresql://', 1)
            else:
                app.logger.warning(
                    "No valid DATABASE_URL found, will use SQLite fallback")
                # Explicitly set database_url to SQLite
                database_url = f'sqlite:///{sqlite_fallback_path}'
    else:
        use_sqlite_fallback = os.getenv(
            'USE_SQLITE_FALLBACK', 'false').lower() == 'true'

    # Enhanced logging for database configuration
    app.logger.info(
        f"Database configuration: SQLite fallback enabled={use_sqlite_fallback}")
    app.logger.info(f"SQLite fallback path: {sqlite_fallback_path}")

    # For Koyeb deployment, ensure we're not using localhost
    if is_koyeb:
        app.logger.info(
            "Running in Koyeb environment, checking database configuration")
        # Always try to get fresh DATABASE_URL from environment in Koyeb
        koyeb_db_url = os.getenv('DATABASE_URL')

        if koyeb_db_url and 'localhost' not in koyeb_db_url:
            app.logger.info(
                "Using DATABASE_URL from Koyeb environment variables")
            database_url = koyeb_db_url
            # Ensure we're using the correct protocol for PostgreSQL
            if database_url.startswith('postgres://'):
                database_url = database_url.replace(
                    'postgres://', 'postgresql://', 1)
                app.logger.info(
                    "Converted postgres:// URL to postgresql:// format in Koyeb environment")
        elif 'localhost' in database_url or not database_url:
            app.logger.warning(
                "Invalid database configuration detected in Koyeb environment")
            app.logger.warning(
                "Falling back to SQLite in Koyeb environment due to invalid database URL")
            database_url = f'sqlite:///{sqlite_fallback_path}'
            use_sqlite_fallback = True

    # Double-check for localhost in production environments
    if (is_production or is_koyeb) and 'localhost' in database_url:
        app.logger.warning(
            "Detected localhost in production environment, forcing SQLite fallback")
        # Try to get DATABASE_URL directly from environment again as a last resort
        env_db_url = os.getenv('DATABASE_URL')
        if env_db_url and 'localhost' not in env_db_url:
            app.logger.info(
                "Using DATABASE_URL from environment as last resort")
            database_url = env_db_url
            # Ensure we're using the correct protocol for PostgreSQL
            if database_url.startswith('postgres://'):
                database_url = database_url.replace(
                    'postgres://', 'postgresql://', 1)
        else:
            database_url = f'sqlite:///{sqlite_fallback_path}'
            use_sqlite_fallback = True

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLITE_FALLBACK_URI'] = f'sqlite:///{sqlite_fallback_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure database connection options with more resilient settings for cloud deployment
    engine_options = {
        'pool_pre_ping': True,  # Verify connections before using them
        'pool_timeout': 30,     # Wait up to 30 seconds for a connection
        'pool_recycle': 1800,   # Recycle connections after 30 minutes
        'pool_size': 5,         # Maintain 5 connections in the pool
        'max_overflow': 10      # Allow up to 10 overflow connections
    }

    # Only add connect_args for non-Supabase connections
    # Some managed PostgreSQL services don't support all these parameters
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

    # Create database tables with error handling
    with app.app_context():
        try:
            app.logger.info("Attempting to create database tables")
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            # If we're in Koyeb and PostgreSQL fails, try SQLite fallback
            if is_koyeb and use_sqlite_fallback:
                app.logger.warning("Attempting to use SQLite fallback")
                try:
                    # Switch to SQLite
                    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_FALLBACK_URI']
                    app.logger.info(
                        f"Switched to SQLite fallback: {app.config['SQLITE_FALLBACK_URI']}")
                    # Recreate engine with new connection string
                    db.get_engine(app, bind=None).dispose()
                    db.create_all()
                    app.logger.info(
                        "Successfully created tables with SQLite fallback")
                except Exception as sqlite_error:
                    app.logger.error(
                        f"SQLite fallback also failed: {str(sqlite_error)}")
            app.logger.warning(
                "Continuing with application startup despite database issues")

    # Register blueprints
    app.register_blueprint(auth_router, url_prefix='/login', name='auth_login')
    app.register_blueprint(user_router, url_prefix='/users')
    app.register_blueprint(account_router, url_prefix='/accounts')
    app.register_blueprint(transaction_router, url_prefix='/transactions')

    # Root route
    @app.route('/')
    def index():
        # Check database connection status with improved error handling
        db_status = "connected"
        db_error = None
        connection_attempts = 0
        max_attempts = 3

        # Try multiple times to connect to the database
        while connection_attempts < max_attempts:
            try:
                connection_attempts += 1
                app.logger.info(
                    f"Root route: Database connection attempt {connection_attempts}/{max_attempts}")

                with db.engine.connect() as connection:
                    pass
                break  # Connection successful, exit the loop
            except Exception as e:
                if connection_attempts >= max_attempts:
                    db_status = "disconnected"
                    db_error = str(e)
                    app.logger.error(
                        f"Database connection error on index route after {max_attempts} attempts: {str(e)}")
                else:
                    app.logger.warning(
                        f"Root route: Connection attempt {connection_attempts} failed, retrying...")
                    import time
                    time.sleep(1)  # Wait 1 second before retrying

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
    app.register_blueprint(auth_router, url_prefix='/login', name='auth_login')
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
        connection_attempts = 0
        max_attempts = 3

        # Try multiple times to connect to the database
        while connection_attempts < max_attempts:
            try:
                connection_attempts += 1
                app.logger.info(
                    f"Diagnostics: Database connection attempt {connection_attempts}/{max_attempts}")

                start_time = datetime.datetime.now()
                with db.engine.connect() as connection:
                    connection_time = (datetime.datetime.now() -
                                       start_time).total_seconds()
                break  # Connection successful, exit the loop
            except Exception as e:
                if connection_attempts >= max_attempts:
                    db_status = "disconnected"
                    db_error = str(e)
                    app.logger.error(
                        f"Database connection error on diagnostics route after {max_attempts} attempts: {str(e)}")
                else:
                    app.logger.warning(
                        f"Diagnostics: Connection attempt {connection_attempts} failed, retrying...")
                    import time
                    time.sleep(1)  # Wait 1 second before retrying

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
        max_retries = 10  # Increased from 5 to 10 for more resilience
        retry_delay = 5   # Seconds to wait between retries
        retries = max_retries
        using_sqlite_fallback = False

        # Log database initialization start
        app.logger.info("Starting database initialization process")
        app.logger.info(
            f"Current environment: Koyeb={is_koyeb}, Production={is_production}")
        app.logger.info(
            f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0].split(':')[0]}:****@{app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'unknown'}")
        app.logger.info(f"SQLite fallback enabled: {use_sqlite_fallback}")

        # For Koyeb, verify DATABASE_URL is set correctly
        if is_koyeb:
            current_db_url = app.config['SQLALCHEMY_DATABASE_URI']
            # Check if we have a valid PostgreSQL URL or if we're already using SQLite
            is_valid_postgres = current_db_url.startswith(
                'postgresql://') and 'localhost' not in current_db_url
            is_valid_sqlite = current_db_url.startswith('sqlite:///')

            if not (is_valid_postgres or is_valid_sqlite):
                app.logger.error(
                    "CRITICAL ERROR: Invalid database configuration in Koyeb environment")
                app.logger.info(
                    "Attempting to recover correct DATABASE_URL from environment")

                # Try to get DATABASE_URL directly from environment again
                koyeb_db_url = os.getenv('DATABASE_URL')
                if koyeb_db_url and 'localhost' not in koyeb_db_url:
                    app.logger.info(
                        "Successfully recovered DATABASE_URL from environment")
                    # Update the database URL
                    if koyeb_db_url.startswith('postgres://'):
                        koyeb_db_url = koyeb_db_url.replace(
                            'postgres://', 'postgresql://', 1)
                    app.config['SQLALCHEMY_DATABASE_URI'] = koyeb_db_url
                    app.logger.info(
                        f"Updated database URL: {koyeb_db_url.split('@')[0].split(':')[0]}:****@{koyeb_db_url.split('@')[1] if '@' in koyeb_db_url else 'unknown'}")

                    # Reinitialize db with new connection string
                    db.init_app(app)
                    using_sqlite_fallback = False
                else:
                    app.logger.warning(
                        "Could not recover valid DATABASE_URL, will use SQLite fallback")
                    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_FALLBACK_URI']
                    using_sqlite_fallback = True

                    # Reinitialize db with SQLite
                    db.init_app(app)

        while retries > 0:
            try:
                # Test database connection with more detailed logging
                masked_url = app.config['SQLALCHEMY_DATABASE_URI']
                if '@' in masked_url:
                    parts = masked_url.split('@')
                    auth_parts = parts[0].split(':')
                    if len(auth_parts) > 1:  # Fixed condition to properly mask password
                        masked_url = f"{auth_parts[0]}:****@{parts[1]}"

                app.logger.info(
                    f"Attempt {max_retries - retries + 1}/{max_retries}: Connecting to database at: {masked_url}")

                # Test connection before creating tables
                connection = db.engine.connect()
                connection.close()
                app.logger.info("Successfully connected to the database")

                # Initialize database tables with error handling
                try:
                    db.create_all()
                    app.logger.info("Database tables created successfully")
                except Exception as table_error:
                    app.logger.error(
                        f"Error creating database tables: {str(table_error)}")
                    raise

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
                # Log more detailed error information for debugging
                app.logger.warning(
                    f"Database connection attempt failed: {str(e)}")
                app.logger.warning(
                    f"Current database URL: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0].split(':')[0]}:****@{app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'unknown'}")

                if retries == 0:
                    app.logger.error(
                        f"Failed to connect to database after {max_retries} attempts: {str(e)}")

                    # Try SQLite fallback if PostgreSQL connection fails in production/Koyeb
                    if (is_production or is_koyeb) and not using_sqlite_fallback:
                        app.logger.warning(
                            "Attempting to use SQLite as fallback database")
                        try:
                            # Switch to SQLite database
                            app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_FALLBACK_URI']
                            using_sqlite_fallback = True
                            app.logger.info(
                                f"Switched to SQLite fallback: {app.config['SQLITE_FALLBACK_URI']}")

                            # Reinitialize database with SQLite
                            db.init_app(app)

                            # Create tables in SQLite
                            db.create_all()
                            app.logger.info(
                                "Successfully switched to SQLite fallback database")

                            # Reset retries to try again with SQLite
                            retries = 3
                            continue
                        except Exception as sqlite_error:
                            app.logger.error(
                                f"SQLite fallback also failed: {str(sqlite_error)}")
                            # Continue without database in production
                            if is_production or is_koyeb:
                                app.logger.warning(
                                    "Running in production mode with limited functionality due to database connection failure")
                                break
                        except Exception as sqlite_error:
                            app.logger.error(
                                f"SQLite fallback also failed: {str(sqlite_error)}")

                    # In production, we might want to continue without the database rather than crashing
                    if is_production or is_koyeb:
                        app.logger.error(
                            "Running in production mode without database. API will have limited functionality.")
                        break
                    else:
                        app.logger.error(
                            "Not in production mode, raising exception to prevent startup with broken database")
                        raise

                # Exponential backoff: increase wait time with each retry
                current_delay = retry_delay * (max_retries - retries)
                app.logger.warning(
                    f"Retrying in {current_delay} seconds... ({retries} attempts left)")
                import time
                time.sleep(current_delay)
            else:
                app.logger.info(
                    "Database connection and initialization completed successfully")
                break  # Break the loop if connection is successful

    return app


# Wrap app creation in try-except to handle any initialization errors
try:
    # Log startup information to help with debugging
    import logging
    logging.info("Starting RevoBank API application")
    logging.info(
        f"Environment variables: KOYEB={os.getenv('KOYEB')}, ENVIRONMENT={os.getenv('ENVIRONMENT')}")
    logging.info(
        f"DATABASE_URL is {'set' if os.getenv('DATABASE_URL') else 'not set'}")

    if os.getenv('DATABASE_URL'):
        masked_url = os.getenv('DATABASE_URL')
        if '@' in masked_url:
            parts = masked_url.split('@')
            auth_parts = parts[0].split(':')
            if len(auth_parts) > 1:
                masked_url = f"{auth_parts[0]}:****@{parts[1]}"
        logging.info(f"DATABASE_URL value: {masked_url}")

    app = create_app()
    # Log successful app creation
    if hasattr(app, 'logger'):
        app.logger.info("Application successfully created and configured")
except Exception as e:
    # If we can't even create the app, log to stdout and create a minimal app
    import logging
    logging.error(f"Critical error during app creation: {str(e)}")
    logging.error(f"Stack trace:", exc_info=True)

    # Create a minimal app that can at least respond to health checks
    app = Flask(__name__)

    @app.route('/')
    def error_index():
        # Include environment information in error response
        return jsonify({
            'name': 'RevoBank API',
            'status': 'error',
            'error': f"Application failed to initialize properly: {str(e)}",
            'database_info': {
                'connection_status': 'disconnected',
                'error': str(e)
            },
            'environment': {
                'koyeb': os.getenv('KOYEB') == 'true',
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'database_url_set': os.getenv('DATABASE_URL') is not None
            }
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
