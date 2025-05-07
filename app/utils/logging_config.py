import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Setup logging configuration"""
    
    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )
    
    # Configure the application logger
    app_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)
    
    # Configure the error logger (for more severe issues)
    error_handler = RotatingFileHandler(
        'logs/error.log', 
        maxBytes=10485760,  # 10 MB
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Set up flask logger specifically
    app.logger.handlers = []
    app.logger.propagate = True
    
    # If in debug mode, add console output
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.DEBUG)
    
    # Log startup
    app.logger.info('Logging initialized')