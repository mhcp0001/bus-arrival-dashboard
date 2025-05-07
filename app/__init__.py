import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///bus_data.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # Override config if provided
    if config:
        app.config.from_mapping(config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Set up logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/bus_dashboard.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Bus Arrival Dashboard startup')
    
    # Setup database
    with app.app_context():
        db.create_all()
    
    return app