import requests

class WeatherService:
    def __init__(self):
        # Hardcoded API key for development
        self.api_key = "ffd4d9619aa461fc483ca0d2ed3ad271"
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self, city="London"):
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                return self._get_default_weather()
                
            data = response.json()
            return {
                "temperature": round(data['main']['temp']),
                "condition": data['weather'][0]['main'],
                "humidity": data['main']['humidity']
            }
        except Exception as e:
            print(f"Weather API error: {str(e)}")
            return self._get_default_weather()
    
    def _get_default_weather(self):
        """Return default weather data when API call fails"""
        return {
            "temperature": 20,
            "condition": "Unknown",
            "humidity": 50
        }