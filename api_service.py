import requests
from datetime import datetime
import time

class WeatherService:
    def __init__(self):
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self._last_weather = None
        self._last_update = 0
        
    def get_weather(self, city="Orlando,FL,US"):  # Default to Orlando, Florida
        try:
            current_time = time.time()
            
            # Return cached data if it's less than 2 minutes old
            if self._last_weather and (current_time - self._last_update) < 120:
                return self._last_weather
                
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "imperial"  # Use Fahrenheit for US
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=3  # Reduced timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "temperature": round(data['main']['temp']),  # Fahrenheit
                    "condition": data['weather'][0]['main'],
                    "humidity": data['main']['humidity'],
                    "feels_like": round(data['main']['feels_like']),
                    "location": "Florida"
                }
                
                self._last_weather = weather_data
                self._last_update = current_time
                
                return weather_data
            else:
                return self._last_weather if self._last_weather else self._get_default_weather()
                
        except Exception as e:
            print(f"Weather service error: {str(e)}")
            return self._last_weather if self._last_weather else self._get_default_weather()
    
    def _get_default_weather(self):
        return {
            "temperature": 75,  # Default Florida temperature in Fahrenheit
            "condition": "Unknown",
            "humidity": 70,  # Default Florida humidity
            "feels_like": 78,
            "location": "Florida"
        }