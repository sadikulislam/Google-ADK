from typing import List, Dict, Optional
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from google.adk.agents import Agent
from google.adk.tools import AgentTool, FunctionTool
from google.adk.tools.google_search_tool import google_search


# Constants
DEFAULT_SEARCH_RADIUS_METERS = 3000
DEFAULT_RESULT_LIMIT = 5
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT_SECONDS = 25
GEOCODER_USER_AGENT = "travel_inspiration_place_finder"


# Google Search Agent - Provides web search grounding
search_agent = Agent(
    model="gemini-2.0-flash",
    name="google_search_wrapped_agent",
    description="Provides Google search grounding capability for travel queries.",
    instruction="""
        You are a travel information specialist that uses Google search to provide 
        immediate, actionable answers for travelers.
        
        Response Guidelines:
        - Answer questions directly using the google_search grounding tool
        - Provide brief, concise, and actionable information
        - Focus on immediate practical value for tourists and travelers
        - Always format responses as bullet points
        - Highlight what matters most to the user
        - Do NOT ask users to look up information themselves - that's your responsibility
        
        Format:
        - Each response should be in single-sentence bullet points
        - Prioritize actionable items over detailed explanations
        - Be informative and direct
    """,
    tools=[google_search],
)

# Export the search agent as a tool for use by other agents
google_search_grounding = AgentTool(agent=search_agent)


def find_nearby_places_open(
    query: str,
    location: str,
    radius: int = DEFAULT_SEARCH_RADIUS_METERS,
    limit: int = DEFAULT_RESULT_LIMIT,
) -> str:
    try:
        # Step 1: Geocode the location to obtain coordinates
        coordinates = _geocode_location(location)
        if not coordinates:
            return f"Error: Could not find location '{location}'. Please verify the location name."

        lat, lon = coordinates

        # Step 2: Query OpenStreetMap for matching places
        places = _search_places_via_overpass(query, lat, lon, radius, limit)

        if not places:
            return f"No results found for '{query}' near {location}. Try broadening your search or using different terms."

        # Step 3: Format and return results
        return _format_place_results(query, location, places, limit)

    except (GeocoderTimedOut, GeocoderServiceError) as geo_error:
        return f"Geocoding service error while searching for '{location}': {str(geo_error)}"
    except requests.RequestException as req_error:
        return f"Network error while searching for places: {str(req_error)}"
    except Exception as error:
        return (
            f"Unexpected error searching for '{query}' near '{location}': {str(error)}"
        )


def _geocode_location(location: str) -> Optional[tuple[float, float]]:
    geolocator = Nominatim(user_agent=GEOCODER_USER_AGENT)
    result = geolocator.geocode(location)

    if result:
        return (result.latitude, result.longitude)
    return None


def _search_places_via_overpass(
    query: str,
    latitude: float,
    longitude: float,
    radius: int,
    limit: int,
) -> List[Dict]:
    overpass_query = f"""
    [out:json][timeout:{OVERPASS_TIMEOUT_SECONDS}];
    (
      node["name"~"{query}", i](around:{radius},{latitude},{longitude});
      node["amenity"~"{query}", i](around:{radius},{latitude},{longitude});
      node["shop"~"{query}", i](around:{radius},{latitude},{longitude});
      way["name"~"{query}", i](around:{radius},{latitude},{longitude});
      way["amenity"~"{query}", i](around:{radius},{latitude},{longitude});
      way["shop"~"{query}", i](around:{radius},{latitude},{longitude});
    );
    out body {limit};
    """

    response = requests.get(
        OVERPASS_API_URL,
        params={"data": overpass_query},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("elements", [])


def _format_place_results(
    query: str,
    location: str,
    places: List[Dict],
    limit: int,
) -> str:
    output_lines = [f"Top results for '{query}' near {location}:\n"]

    for place in places[:limit]:
        tags = place.get("tags", {})
        name = tags.get("name", "Unnamed place")

        # Extract address components
        street = tags.get("addr:street", "")
        house_number = tags.get("addr:housenumber", "")
        city = tags.get("addr:city", "")

        # Build address string
        address_parts = []
        if house_number and street:
            address_parts.append(f"{house_number} {street}")
        elif street:
            address_parts.append(street)
        if city:
            address_parts.append(city)

        full_address = (
            ", ".join(address_parts) if address_parts else "Address not available"
        )

        output_lines.append(f"- {name} | {full_address}")

    return "\n".join(output_lines)


# Export the location search function as a tool
location_search_tool = FunctionTool(func=find_nearby_places_open)
