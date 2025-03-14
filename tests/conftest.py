import pytest
from run import create_app
from flask import Flask

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    # Create a test client using the Flask application
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def app_context(app):
    """An application context for the tests."""
    with app.app_context():
        yield
        
@pytest.fixture
def request_context(app):
    """A request context for the tests."""
    with app.test_request_context():
        yield