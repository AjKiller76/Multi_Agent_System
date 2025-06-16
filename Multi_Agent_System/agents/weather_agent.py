from google.adk import Agent
from utils.api_clients import get_weather_forecast

class WeatherAgent(Agent):
    """An agent that fetches weather data for a location and date."""
    
    name: str = "weather_agent"

    def run(self, context: dict) -> None:
        spacex_data = context.get("spacex_data")

        if not spacex_data:
            print("! WeatherAgent: Missing spacex_data in context. Skipping.")
            context["error"] = "Cannot fetch weather without launch data."
            return

        location = spacex_data.get("location")
        date_str = spacex_data.get("date")

        if location and date_str:
            try:
                weather_data = get_weather_forecast(location, date_str)
                context["weather_data"] = weather_data
                print(f"> Data from WeatherAgent: {weather_data}")
            except Exception as e:
                context["error"] = f"Weather API error: {e}"
                print(f"! WeatherAgent: Exception occurred - {e}")
        else:
            print("! WeatherAgent: Missing location or date in spacex_data. Skipping.")
            context["error"] = "Missing location or date for weather forecast."
