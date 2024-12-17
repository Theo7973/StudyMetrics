# api_service.py
import requests
from datetime import datetime

class WeatherService:
    def __init__(self):
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"  
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city="New York"):
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'condition': data['weather'][0]['main'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description']
                }
            return None
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None