import os
import sys

# Add current directory to path to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import google.generativeai as genai
from dotenv import load_dotenv

# Import all agents
from agents.planner_agent import PlannerAgent
from agents.spacex_agent import SpaceXAgent
from agents.weather_agent import WeatherAgent
from agents.summary_agent import SummaryAgent


def main():
    # 1. Load environment variables from .env
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

    # 2. Configure the Generative AI model
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # 3. Initialize agents
    planner_agent = PlannerAgent(model=model)
    spacex_agent = SpaceXAgent()
    weather_agent = WeatherAgent()
    summary_agent = SummaryAgent(model=model)

    # 4. Agent Registry (tool name → agent instance)
    agent_registry = {
        "spacex_agent": spacex_agent,
        "weather_agent": weather_agent,
        "summary_agent": summary_agent,
    }

    # 5. Get user goal
    goal = input("Enter your goal: ").strip()
    if not goal:
        print("Goal cannot be empty.")
        return

    context = {"goal": goal}

    # 6. Run Planner to generate plan
    print("> Executing PlannerAgent")
    planner_agent.run(context)
    plan = context.get("plan")

    if not plan:
        print("I'm sorry, I can't fulfill that request with my current capabilities.")
        return

    # 7. Execute agents based on the plan
    for agent_name in plan:
        agent = agent_registry.get(agent_name)
        if not agent:
            print(f"! Warning: Agent '{agent_name}' not found in registry.")
            continue

        print(f"> Executing Agent: {agent_name}")
        agent.run(context)

        if context.get("error"):
            print(f"! Error occurred: {context['error']}")
            break
        print()  # Newline for cleaner output

    # 8. Print final output
    final_summary = context.get("final_summary")
    if final_summary:
        print("--------------------------------------------------")
        print("** Goal Accomplished: Final Summary **")
        print("--------------------------------------------------")
        print(final_summary)
    elif not context.get("error"):
        print("The plan was executed, but no final summary was generated.")


if __name__ == "__main__":
    main()
