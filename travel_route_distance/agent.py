from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.agent_tool import AgentTool


LLM = "gemini-2.0-flash"


distance_calculator_agent = Agent(
    model=LLM,
    name="distance_calculator_agent",
    description="Given a list of city names, uses google_search to find road distances (and optionally travel times) between city pairs. Outputs a JSON adjacency matrix with entries containing distance_km and time_hr.",
    instruction=(
        'Input: {"cities": ["CityA", "CityB", ...], "mode": "distance" or "time"}.\n'
        "Use the google_search tool to get real road distances and estimated travel times between every unique pair of cities. "
        "Output a JSON object where keys are city names, values are maps to every other city, each entry like: "
        '{"CityB": {"distance_km": 120, "time_hr": 1.5}, …} '
        'The matrix must be symmetric, and diagonal entries should be {"distance_km": 0, "time_hr": 0}.'
    ),
    tools=[google_search],
)

distance_tool = AgentTool(agent=distance_calculator_agent)

shortest_path_agent = Agent(
    model=LLM,
    name="shortest_path_agent",
    description="Solves the TSP for the given adjacency matrix, optimized according to mode (distance or time). Outputs route step-by-step and total metric.",
    instruction=(
        'Input: {"matrix": {…}, "mode": "distance" or "time"}. '
        "Apply a nearest neighbor or other approximation algorithm to compute a cycle visiting each city exactly once, returning to the start. "
        'If mode is "distance", minimize sum of distance_km. If mode is "time", minimize sum of time_hr. '
        'Output: {"route": ["CityA","CityC",…,"CityA"], "total_distance_km": …, "total_time_hr": …}.'
    ),
    tools=[distance_tool],
)

shortest_path_tool = AgentTool(agent=shortest_path_agent)

root_agent = Agent(
    model=LLM,
    name="root_agent",
    description="Orchestrates the road-trip planner among given cities, asks user for optimization mode, calculates matrix then TSP route.",
    instruction=(
        'First, validate the input list of cities. If fewer than 3, return an error: "Please provide at least 3 cities". \n'
        'Then ask the user: "Would you like to optimize for shortest distance or shortest time?" Use the answer to set mode. \n'
        'Then call the distance_tool with input {"cities": [...], "mode": selected_mode} to get the adjacency matrix. \n'
        'Then call the shortest_path_tool with input {"matrix": <that_matrix>, "mode": selected_mode} to compute the route. \n'
        "Finally return a markdown summary with the starting/ending city, full route, total distance (km) and total time (hr)."
    ),
    tools=[distance_tool, shortest_path_tool],
)
