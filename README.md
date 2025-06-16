# Multi-Agent AI System Using Google ADK

This project implements a multi-agent AI system using the Google Agent Development Kit (ADK). The system takes a high-level user goal, dynamically creates an execution plan, and routes data between specialized agents to achieve the goal. Each agent enriches the data from the previous one, demonstrating a collaborative, chained workflow.

## System Architecture & Flow

The system operates based on a "Planner-Executor" model. A central orchestrator in `main.py` manages the flow, but the intelligence for ordering tasks comes from a dedicated Planner Agent.

1.  **User Goal**: The user provides a natural language goal (e.g., "Find the next SpaceX launch and its weather forecast to see if it might be delayed").
2.  **Planner Agent**: This agent, powered by Google's Gemini LLM, receives the user's goal. Its job is to analyze the request and create a step-by-step plan. The plan is a simple JSON list of agent names that need to be executed in sequence.
3.  **Orchestrator (`main.py`)**: The main script receives the plan from the Planner. It then iterates through the plan, executing each agent in the specified order.
4.  **Enrichment Agents**:
    *   **`SpaceXAgent`**: Fetches data for the next SpaceX launch.
    *   **`WeatherAgent`**: Takes the location and date from the `SpaceXAgent`'s output, gets its coordinates, and fetches the 5-day weather forecast.
5.  **Data Flow**: Each agent runs within a shared `Context`. An agent reads the necessary information from the context (left by previous agents), performs its task, and writes its new findings back into the context.
6.  **Summary Agent**: The final agent in the chain (also powered by Gemini) reads all the enriched data from the context (launch details, weather forecast) and generates a final, human-readable summary that directly answers the user's original goal.



## Agent Logic

*   **`PlannerAgent`**:
    *   **Input**: User's goal string.
    *   **Logic**: Uses a powerful prompt to instruct the Gemini LLM to act as a dispatcher. It provides the LLM with a list of available "tools" (our other agents) and asks it to return a JSON array representing the execution plan. It is instructed to return an empty list if the goal cannot be achieved with the available tools.
    *   **Output**: A list of agent names (e.g., `["spacex_agent", "weather_agent"]`) stored in the `Context`.

*   **`SpaceXAgent`**:
    *   **Input**: None (it's the first enrichment agent).
    *   **Logic**: Calls the public `r/SpaceX` API to get details about the next upcoming launch. It also makes a secondary call to get the full name of the launchpad location.
    *   **Output**: A dictionary containing launch name, date, and location, stored in the `Context`.

*   **`WeatherAgent`**:
    *   **Input**: Launch data (specifically location and date) from the `Context`.
    *   **Logic**: Uses the OpenWeatherMap API. First, it uses the Geocoding API to convert the launch location name (e.g., "Cape Canaveral") into latitude and longitude. Then, it uses the 5-Day Forecast API to get weather data for those coordinates. It intelligently finds the forecast closest to the launch date.
    *   **Output**: A dictionary containing a formatted weather forecast string, stored in the `Context`.

*   **`SummaryAgent`**:
    *   **Input**: All data from the `Context` (launch details, weather forecast).
    *   **Logic**: Uses the Gemini LLM. It's prompted to synthesize all the provided data into a concise summary that assesses the potential for a weather-related delay.
    *   **Output**: The final, user-facing summary string.

## APIs Used

*   **Google Gemini**: For the Planner and Summarizer agents.
*   **r/SpaceX API (v5)**: A free, public, and unofficial API for all things SpaceX. Used to get launch data.
*   **OpenWeatherMap API**: Used for geocoding location names to coordinates and for fetching weather forecasts. Requires a free API key.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd multi_agent_system_adk
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    *   Copy the example `.env` file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your API keys:
        *   `GOOGLE_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/app/apikey).
        *   `OPENWEATHER_API_KEY`: Get from [OpenWeatherMap](https://home.openweathermap.org/api_keys).

## How to Run

Execute the `main.py` script from your terminal. It will prompt you to enter a goal.

```bash
python main.py
```

**Example Interaction:**

```
Enter your goal: Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed.

> Running Planner...
> Plan received: ['spacex_agent', 'weather_agent', 'summary_agent']

> Executing Agent: spacex_agent
> Data from SpaceXAgent: {'name': 'Starlink Group 9-1', 'date': '2024-05-30T02:30:00.000Z', 'location': 'Cape Canaveral Space Force Station'}

> Executing Agent: weather_agent
> Data from WeatherAgent: {'forecast': 'On 2024-05-30, the weather is expected to be: broken clouds with a temperature of 26.5°C.'}

> Executing Agent: summary_agent
> Generating final summary...

--------------------------------------------------
**Goal Accomplished: Final Summary**
--------------------------------------------------
The next SpaceX launch is Starlink Group 9-1, scheduled for May 30, 2024, from Cape Canaveral Space Force Station. The weather forecast for that day indicates broken clouds with a temperature of approximately 26.5°C. Based on this forecast, there are no immediate, significant weather concerns that would suggest a high probability of delay.
```
