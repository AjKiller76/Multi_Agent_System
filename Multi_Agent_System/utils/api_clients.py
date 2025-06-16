import os
import requests
from datetime import datetime, timedelta

def get_next_spacex_launch():
    """Fetches the next SpaceX launch and its launchpad details."""
    try:
        # Get next launch
        launch_url = "https://api.spacexdata.com/v5/launches/next"
        response = requests.get(launch_url)
        response.raise_for_status()
        launch_data = response.json()

        # Get launchpad details for a more user-friendly location name
        launchpad_id = launch_data.get("launchpad")
        launchpad_url = f"https://api.spacexdata.com/v4/launchpads/{launchpad_id}"
        pad_response = requests.get(launchpad_url)
        pad_response.raise_for_status()
        pad_data = pad_response.json()

        return {
            "name": launch_data.get("name"),
            "date": launch_data.get("date_utc"),
            "location": pad_data.get("full_name", "Unknown Location")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching SpaceX data: {e}")
        return None

def get_weather_forecast(location: str, date_str: str):
    """Fetches weather forecast for a given location and date."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not found in .env file.")

    try:
        # 1. Geocode location to lat/lon
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={api_key}"
        geo_res = requests.get(geo_url)
        geo_res.raise_for_status()
        geo_data = geo_res.json()
        if not geo_data:
            return {"error": f"Could not find coordinates for {location}."}
        
        lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

        # 2. Get 5-day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        forecast_res = requests.get(forecast_url)
        forecast_res.raise_for_status()
        forecast_data = forecast_res.json()

        # 3. Find the forecast closest to the launch date
        launch_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        
        for forecast in forecast_data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            if forecast_date == launch_date:
                weather_desc = forecast['weather'][0]['description']
                temp = forecast['main']['temp']
                return {
                    "forecast": f"On {forecast_date}, the weather is expected to be: {weather_desc} with a temperature of {temp}°C."
                }

        return {"forecast": "No forecast available for the specific launch date (may be >5 days away)."}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {"error": "Failed to retrieve weather data."}