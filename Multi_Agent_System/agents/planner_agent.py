import google.generativeai as genai
import json
from google.adk import Agent


class PlannerAgent(Agent):
    """An agent that uses a Gemini model to generate a plan based on a user goal."""
    
    name: str = "planner_agent"

    def __init__(self, model: genai.GenerativeModel):
        self._model = model

    def run(self, context: dict) -> None:
        goal = context.get("goal")
        if not goal:
            print("No goal found in context. Skipping planning.")
            context["plan"] = []
            return

        prompt = f"""
        You are a planner for a multi-agent system. Your job is to take a user's goal
        and create a plan by choosing from a list of available tools (agents).

        Available Tools:
        - "spacex_agent": Use this to get information about the next SpaceX launch.
        - "weather_agent": Use this to get the weather forecast for a specific location and date. Requires prior information about the location and date.
        - "summary_agent": Use this to create a final summary for the user after all other data has been gathered.

        User Goal: "{goal}"

        Based on the user's goal, create a JSON array of the tools to use in the correct order.
        The "summary_agent" should always be last if it is needed.
        If the goal cannot be fulfilled with the available tools, return an empty JSON array [].

        Example 1:
        User Goal: "Find the next spaceX launch and its weather."
        Plan: ["spacex_agent", "weather_agent", "summary_agent"]

        Example 2:
        User Goal: "Tell me about the next spaceX mission."
        Plan: ["spacex_agent", "summary_agent"]
        
        Example 3:
        User Goal: "What is the price of Bitcoin?"
        Plan: []

        Now, create the plan for the provided user goal.
        Response:
        """

        print("> Running Planner...")

        try:
            response = self._model.generate_content(prompt)
            plan_str = response.text.strip()

            # Sanitize and extract valid JSON array
            if "```" in plan_str:
                plan_str = plan_str.replace("```json", "").replace("```", "").strip()

            plan = json.loads(plan_str)

            if isinstance(plan, list) and all(isinstance(item, str) for item in plan):
                print(f"> Plan received: {plan}")
                context["plan"] = plan
            else:
                print(f"! Invalid plan structure. Expected list of strings, got: {plan}")
                context["plan"] = []

        except Exception as e:
            print(f"! Error during planning: {e}")
            context["plan"] = []
