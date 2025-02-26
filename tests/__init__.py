"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""

import sys
from flask import Flask
from service import config
from service.common import log_handlers


############################################################
# Initialize the Flask instance
############################################################
def create_app():
    """Initialize the core application."""
    # Create Flask application
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize Plugins
    # pylint: disable=import-outside-toplevel
    from service.models import db

    db.init_app(app)

    with app.app_context():
        # Dependencies require we import the routes AFTER the Flask app is created
        # pylint: disable=wrong-import-position, wrong-import-order, unused-import
        from service import routes, models  # noqa: F401 E402
        from service.common import error_handlers, cli_commands  # noqa: F401, E402

        try:
            models.init_db()  # make our sqlalchemy tables
        except Exception as error:  # pylint: disable=broad-except
            app.logger.critical("%s: Cannot continue", error)
            # gunicorn requires exit code 4 to stop spawning workers when they die
            sys.exit(4)

        # Set up logging for production
        log_handlers.init_logging(app, "gunicorn.error")

        app.logger.info(70 * "*")
        app.logger.info("  P R O D U C T   S E R V I C E  ".center(70, "*"))
        app.logger.info(70 * "*")

        app.logger.info("Service initialized!")

        return app
