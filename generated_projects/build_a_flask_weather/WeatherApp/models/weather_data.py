
class WeatherData:
    def __init__(self):
        self.data = {}

    def get_weather(self, city):
        if city in self.data:
            return self.data[city]
        else:
            response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_API_KEY")
            data = json.loads(response.text)
            self.data[city] = data
            return data

    def get_all_weather(self):
        return list(self.data.values())

    def clear_data(self):
        self.data = {}
