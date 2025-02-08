import requests
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("ffd4d9619aa461fc483ca0d2ed3ad271")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city="London"):
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            return {
                "temperature": round(data['main']['temp']),
                "condition": data['weather'][0]['main'],
                "humidity": data['main']['humidity']
            }
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return None