
import logging
from weather_app import app

class Logger:
    def __init__(self):
        self.logger = logging.getLogger('weather_app')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_weather_request(self, city):
        self.logger.info(f'Weather request received for {city}')

    def log_all_weather_request(self):
        self.logger.info('All weather data requested')

    def log_clear_data(self):
        self.logger.info('Weather data cleared')
