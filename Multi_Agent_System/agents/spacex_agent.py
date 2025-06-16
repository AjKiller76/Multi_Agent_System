from google.adk import Agent
from utils.api_clients import get_next_spacex_launch

class SpaceXAgent(Agent):
    """An agent that fetches data about the next SpaceX launch."""
    
    name: str = "spacex_agent"

    def run(self, context: dict) -> None:
        try:
            launch_data = get_next_spacex_launch()
            if launch_data:
                context["spacex_data"] = launch_data
                print(f"> Data from SpaceXAgent: {launch_data}")
            else:
                context["error"] = "Failed to fetch SpaceX data."
                print("! Error: No data received from SpaceX API.")
        except Exception as e:
            context["error"] = f"Exception in SpaceXAgent: {e}"
            print(f"! Exception occurred in SpaceXAgent: {e}")
