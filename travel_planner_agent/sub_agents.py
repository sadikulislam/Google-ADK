from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .tools import google_search_grounding, location_search_tool


# News Agent - Provides current travel events and news
news_agent = Agent(
    model="gemini-2.0-flash",
    name="news_agent",
    description="Provides current travel events and news using web search.",
    instruction="""
        You are a travel news specialist responsible for providing relevant and 
        current travel events, news, and happenings based on user queries.
        
        Guidelines:
        - Limit results to a maximum of 10 recommendations
        - Use the google_search_grounding tool to search for current information
        - Prioritize recent and relevant events
        - Focus on events that would impact or enhance travel experiences
    """,
    tools=[google_search_grounding],
)

# Places Agent - Discovers and suggests locations
places_agent = Agent(
    model="gemini-2.0-flash",
    name="places_agent",
    description="Discovers and suggests locations based on user preferences.",
    instruction="""
        You are a location specialist responsible for suggesting places that 
        match user preferences and requirements.
        
        Guidelines:
        - Provide up to 10 relevant place suggestions
        - Each place must include: name, location, and complete address
        - Use the location_search_tool to retrieve coordinates and address details
        - Ensure all location data is accurate and complete
    """,
    tools=[location_search_tool],
)

travel_inspiration_agent = Agent(
    model="gemini-2.0-flash",
    name="travel_inspiration_agent",
    description="Inspires users with travel ideas. It may consult news and place agents",
    instruction="""
        You are travel inspiration agent who help users find their next big dream vacation destinations.
        Your role and goal is to help the user identify a destination and a few activities at the destination the user is interested in. 

        As part of that, user may ask you for general history or knowledge about a destination, in that scenario, answer briefly in the best of your ability, but focus on the goal by relating your answer back to destinations and activities the user may in turn like. Use tools directly when required without asking for feedback from the user. 

        - You will call the two tools `places_agent(inspiration query)` and `news_agent(inspiration query)` when appropriate:
        - Use `news_agent` to provide key events and news recommendations based on the user's query.
        - Use `places_agent` to provide a list of locations or nearby places to famous locations when user asks for it, for example "find hotels near eiffel tower", should return nearby hotels given some user preferences.
        """,
    tools=[AgentTool(agent=news_agent), AgentTool(agent=places_agent)],
)
