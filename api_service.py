import requests
import time
import logging
from error_handler import ErrorHandler

class WeatherService:
    def __init__(self):
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self._last_weather = None
        self._last_update = 0
        
    @ErrorHandler.handle_api_error
    def get_weather(self, city="Orlando"):
        try:
            current_time = time.time()
            
            # Return cached data if valid
            if self._last_weather and (current_time - self._last_update) < 120:
                return self._last_weather
                
            # Define parameters FIRST before any potential errors
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "imperial"
            }
            
            # Make API call
            response = requests.get(self.base_url, params=params, timeout=3)
            response.raise_for_status()
            
            # Process response
            data = response.json()
            weather_data = {
                "temperature": round(data['main']['temp']),
                "condition": data['weather'][0]['main'],
                "humidity": data['main']['humidity'],
                "feels_like": round(data['main']['feels_like'])
            }
            
            # Update cache
            self._last_weather = weather_data
            self._last_update = current_time
            return weather_data
            
        except Exception as e:
            logging.error(f"Failed to fetch weather: {str(e)}")
            return self._get_default_weather()
    
    def _get_default_weather(self):
        return {
            "temperature": 75,
            "condition": "Unknown",
            "humidity": 70,
            "feels_like": 78
        }