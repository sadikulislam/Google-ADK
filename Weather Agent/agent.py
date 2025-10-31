from google.adk.agents import Agent
from . import prompt
from datetime import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(location: str) -> dict:
    """
    Fetch current weather information for a given city.
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": API_KEY, "units": "metric"}
    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        return {
            "status": "success",
            "weather_desc": weather_desc,
            "temperature": temp,
            "location": location,
            "report": f"The weather in {location} is {weather_desc} with a temperature of {temp}°C.",
        }
    else:
        return {
            "status": "error",
            "report": f"Weather information for '{location}' is not available.",
        }


def get_timezone_from_city(city: str) -> str:
    """
    Get the IANA timezone string (like 'Asia/Dhaka') from a city name.
    """
    try:
        geolocator = Nominatim(user_agent="weather_time_agent")
        location = geolocator.geocode(city)
        if location:
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            return timezone
    except Exception:
        pass
    return None


def get_current_time(location: str) -> dict:
    """
    Returns the current time in a specified city or timezone.
    """
    tz_name = get_timezone_from_city(location) or location
    try:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        return {
            "status": "success",
            "timezone": tz_name,
            "report": f"The current time in {location} is {now.strftime('%Y-%m-%d %I:%M %p (%Z)')}.",
        }
    except Exception:
        return {
            "status": "error",
            "report": (
                f"Could not find timezone for '{location}'. "
                "Please try using a valid city or timezone name (e.g., New York, Asia/Dhaka)."
            ),
        }


def get_weather_and_time(location: str) -> dict:
    """
    Combines weather and time info into a single friendly response.
    """
    weather = get_weather(location)
    time = get_current_time(location)

    if weather["status"] == "success" and time["status"] == "success":
        return {
            "status": "success",
            "report": (
                f"Right now in {location}, it's {time['report'].split('is')[1].strip()} "
                f"The weather is {weather['weather_desc']} with a temperature of {weather['temperature']}°C."
            ),
        }
    else:
        return {
            "status": "error",
            "report": "Unable to retrieve complete data for that location.",
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="An intelligent agent that provides real-time weather and time updates for any city worldwide.",
    instruction=prompt.weather_instruction,
    tools=[get_weather, get_current_time, get_weather_and_time],
)
