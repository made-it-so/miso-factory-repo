
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Define a route for getting weather information
@app.route('/weather', methods=['GET'])
def get_weather():
    # Get the city name from the query parameter
    city_name = request.args.get('city')

    # Check if the city name is provided
    if not city_name:
        return jsonify({'error': 'City name required'}), 400

    try:
        # Make a GET request to an external weather API (replace with your actual API)
        response = requests.get(f'https://api.weather.com/{city_name}')

        # Check if the API returned valid data
        if response.status_code == 200:
            return response.json(), 200
        else:
            return jsonify({'error': 'Failed to retrieve weather information'}), 500
    except Exception as e:
        # Handle any exceptions that occur during API calls or parsing
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
