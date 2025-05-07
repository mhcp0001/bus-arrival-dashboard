from flask import render_template, current_app
from app import create_app
from app.services.scheduler import bus_scheduler
from app.utils.logging_config import setup_logging

# Create the Flask application
app = create_app()

# Set up logging
setup_logging(app)

# Initialize scheduler with the app
bus_scheduler.init_app(app)

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')