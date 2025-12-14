"""
Flask Application Factory
-------------------------
Responsible for:
- Creating the Flask app instance
- Loading configuration
- Initializing database connections
- Registering routes
"""

from flask import Flask

from app.config import init_app
from app.database import MySQLDatabase


def create_app():
    """
    Application factory function.
    Creates and configures the Flask app.
    """

    app = Flask(__name__)

    # Load configuration
    init_app(app)

    # Initialize MySQL connection pool
    with app.app_context():
        MySQLDatabase.initialize_pool()

    # Register route blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.meal_routes import meal_bp
    from app.routes.feedback_routes import feedback_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(meal_bp)
    app.register_blueprint(feedback_bp)

    return app
