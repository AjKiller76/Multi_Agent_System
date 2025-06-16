import google.generativeai as genai
from google.adk import Agent

class SummaryAgent(Agent):
    """An agent that summarizes all gathered information for the user."""
    
    name: str = "summary_agent"

    def __init__(self, model: genai.GenerativeModel):
        self._model = model

    def run(self, context: dict) -> None:
        print("> Generating final summary...")

        goal = context.get("goal", "N/A")
        spacex_data = context.get("spacex_data", "Not available")
        weather_data = context.get("weather_data", "Not available")

        prompt = f"""
        You are a helpful assistant. Your task is to synthesize the following information into a
        concise and clear summary that directly answers the user's original goal.

        User's Goal: "{goal}"

        Available Data:
        - SpaceX Launch Data: {spacex_data}
        - Weather Forecast Data: {weather_data}

        Based on all this information, provide a final, user-friendly summary. If the weather data
        suggests clear conditions, state that. If it suggests potential issues (like storms or high winds),
        mention that it might affect the launch. If data is missing, state that.
        """

        try:
            response = self._model.generate_content(prompt)
            final_summary = response.text.strip()
            context["final_summary"] = final_summary
            print(f"> Final Summary Generated:\n{final_summary}")
        except Exception as e:
            context["error"] = f"Exception in SummaryAgent: {e}"
            print(f"! Exception occurred in SummaryAgent: {e}")
