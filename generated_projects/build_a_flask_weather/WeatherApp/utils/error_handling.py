
from weather_app.utils.logging import Logger
import logging

class ErrorHandling:
    def __init__(self):
        self.logger = Logger()

    def handle_exception(self, exception):
        self.logger.log_error(exception)
        return jsonify({"error": "An unexpected error occurred"}), 500

    def handle_invalid_request(self, request_data):
        return jsonify({"error": "Invalid request data"}), 400
