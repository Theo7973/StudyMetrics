import requests
import os
from dotenv import load_dotenv

class WeatherService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ffd4d9619aa461fc483ca0d2ed3ad271")
        if not self.api_key:
            raise ValueError("Weather API key not found in environment variables")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city="London"):
        try:
            if not self.api_key:
                return None
                
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()
            
            return {
                "temperature": round(data['main']['temp']),
                "condition": data['weather'][0]['main'],
                "humidity": data['main']['humidity']
            }
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return None