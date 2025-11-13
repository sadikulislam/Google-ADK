from google.adk.agents import Agent
from .prompt import root_agent_instruction
from travel_planner_agent.sub_agents import travel_inspiration_agent


# Root Agent - Main orchestrator for the travel planning system
root_agent = Agent(
    model="gemini-2.0-flash",
    name="travel_planner_main",
    description=(
        "An intelligent, context-aware travel planning assistant that provides "
        "personalized information and suggestions based on user preferences."
    ),
    instruction=root_agent_instruction,
    sub_agents=[travel_inspiration_agent],
)
