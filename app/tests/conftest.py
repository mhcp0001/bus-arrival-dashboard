import pytest
from app import create_app, db

@pytest.fixture
def app():
    """Create and configure a Flask app for testing"""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()