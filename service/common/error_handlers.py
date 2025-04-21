from flask import current_app as app
from service.routes import api
from service.models import DataValidationError
from . import status


@api.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    message = str(error)
    app.logger.error(message)
    return {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST
