from google.genai import Client
from google.adk.agents.llm_agent import Agent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types
import os
import json
from typing import Optional
from datetime import datetime

try:
    from google.adk.agents.remote_a2a_agent import (
        AGENT_CARD_WELL_KNOWN_PATH,
        RemoteA2aAgent,
    )
except ImportError:
    AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent.json"
    RemoteA2aAgent = None

attractions_agent = Agent(
    model="gemini-2.5-flash",
    name="attractions_agent",
    description="Provides tourist attractions info for a given city.",
    instruction="""
    You are responsible for suggesting popular tourist attractions,
    sightseeing spots, and local activities for the given city.
    Provide concise and relevant recommendations to help the user plan their trip.
    """,
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF
            )
        ]
    )
)

# --- Load mock flight dataset ---
FLIGHTS_JSON_PATH = os.path.join(os.path.dirname(__file__), "flights_dataset.json")

with open(FLIGHTS_JSON_PATH, "r") as f:
    flights_data = json.load(f)

def _parse_flight_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value

    for fmt in ("%m-%d %H:%M", "%m-%d %H:%M-%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def query_flights(dep_city=None, arr_city=None, date=None, start_date=None, end_date=None, month=None):
    results = []
    for flight in flights_data:
        dep_time_str = flight["departure_time"]
        dep_time = _parse_flight_datetime(dep_time_str)
        if dep_time is None:
            continue

        if dep_city and flight.get("departure_city", "").lower() != dep_city.lower():
            continue
        if arr_city and flight.get("arrival_city", "").lower() != arr_city.lower():
            continue

        if start_date and end_date:
            start = _parse_flight_datetime(start_date)
            end = _parse_flight_datetime(end_date)
            if start is None or end is None:
                continue
            if not (start <= dep_time <= end):
                continue

        if month:
            if dep_time.month != int(month):
                continue

        results.append(flight)

    return results

def query_flights_simple(dep_city: str = "", arr_city: str = "", date: str = "") -> list:
    dep_city = dep_city or None
    arr_city = arr_city or None
    date = date or None
    return query_flights(dep_city=dep_city, arr_city=arr_city, date=date)

flight_agent = Agent(
    model="gemini-2.5-flash",
    name="flight_agent",
    description="Provides flight information from the mock flight dataset using city names.",
    instruction="""
      You are a Flight Information agent. When asked for flights between cities on a certain date, 
      query the mock flight dataset and provide a clear summary of matching flights,
      including airline, flight number, departure/arrival cities and times, and status.
      If no flights match, politely tell the user that no flights were found.
      Assume the user provides city names, not airport codes.
    """,
    tools=[query_flights_simple],  
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    )
)