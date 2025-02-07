
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_weather(self, city="New York"):
        try:
            params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return {
                'condition': data['weather'][0]['main'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description']
            }
        except Exception as e:
            logger.error(f"Weather API failure: {str(e)}")
            return {'error': 'Weather service unavailable'}