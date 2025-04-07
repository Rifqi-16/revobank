from flask import Flask, jsonify
from flask_migrate import Migrate
from db.database import db
import os
import datetime


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'revobank_secret_key')
    # Initialize database configuration
    is_koyeb = os.getenv('KOYEB') == 'true'
    database_url = os.getenv('DATABASE_URL')

    # Configure SQLite fallback path
    sqlite_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'revobank.db')

    # Handle database URL configuration
    if is_koyeb:
        if not database_url:
            app.logger.warning(
                "No DATABASE_URL found in Koyeb environment, using SQLite fallback")
            database_url = f'sqlite:///{sqlite_path}'
        elif 'localhost' in database_url:
            app.logger.warning(
                "Invalid localhost DATABASE_URL in Koyeb environment, using SQLite fallback")
            database_url = f'sqlite:///{sqlite_path}'
        elif database_url.startswith('postgres://'):
            database_url = database_url.replace(
                'postgres://', 'postgresql://', 1)
            app.logger.info(
                "Converted postgres:// URL to postgresql:// format")
    else:
        if not database_url:
            app.logger.info(
                "No DATABASE_URL found, using SQLite for local development")
            database_url = f'sqlite:///{sqlite_path}'

    # Mask sensitive information in database URL for logging
    masked_url = database_url
    if '@' in masked_url:
        parts = masked_url.split('@')
        auth_parts = parts[0].split(':')
        if len(auth_parts) > 1:
            masked_url = f"{auth_parts[0]}:****@{parts[1]}"
    app.logger.info(f"Using database URL: {masked_url}")

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with error handling
    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        if not database_url.startswith('sqlite:///'):
            app.logger.warning("Attempting SQLite fallback")
            database_url = f'sqlite:///{sqlite_path}'
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            try:
                db.init_app(app)
                with app.app_context():
                    db.create_all()
                app.logger.info(
                    "SQLite fallback database initialized successfully")
            except Exception as e:
                app.logger.error(
                    f"Failed to initialize SQLite fallback: {str(e)}")
                raise

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    from routers.user_router import user_bp
    from routers.auth_router import auth_bp
    from routers.account_router import account_bp
    from routers.transaction_router import transaction_bp

    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(account_bp, url_prefix='/api/accounts')
    app.register_blueprint(transaction_bp, url_prefix='/api/transactions')

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy", "timestamp": datetime.datetime.utcnow()})

    return app


# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
