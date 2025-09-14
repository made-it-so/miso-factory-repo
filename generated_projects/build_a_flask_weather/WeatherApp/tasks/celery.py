
from celery import Celery
from weather_app.models.weather_data import WeatherData

app = Flask(__name__)
celery_app = Celery('tasks', broker='amqp://guest:guest@localhost//')

@celery_app.task
def get_weather_task(city):
    try:
        data = WeatherData().get_weather(city)
        return jsonify(data)
    except Exception as e:
        handle_exception(e)

@celery_app.task
def clear_data_task():
    try:
        data = WeatherData().clear_data()
        return jsonify({'message': 'Data cleared successfully'})
    except Exception as e:
        handle_exception(e)

if __name__ == '__main__':
    celery_app.start()
