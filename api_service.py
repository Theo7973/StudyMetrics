import requests
from datetime import datetime
import time

class WeatherService:
    def __init__(self):
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self._last_weather = None
        self._last_update = 0
        
    def get_weather(self, city="London"):
        """Get current weather with improved error handling and caching"""
        try:
            current_time = time.time()
            
            # Return cached data if it's less than 5 minutes old
            if self._last_weather and (current_time - self._last_update) < 300:
                return self._last_weather
                
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use metric units
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=5  # Add timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "temperature": round(data['main']['temp'], 1),
                    "condition": data['weather'][0]['main'],
                    "humidity": data['main']['humidity'],
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                
                # Cache the results
                self._last_weather = weather_data
                self._last_update = current_time
                
                return weather_data
            else:
                print(f"Weather API error: {response.status_code}")
                return self._last_weather if self._last_weather else self._get_default_weather()
                
        except Exception as e:
            print(f"Weather service error: {str(e)}")
            return self._last_weather if self._last_weather else self._get_default_weather()
    
    def _get_default_weather(self):
        """Return default weather data"""
        return {
            "temperature": 20,
            "condition": "Unknown",
            "humidity": 50,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }