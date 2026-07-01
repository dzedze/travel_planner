from google.genai import Client
from google.adk.agents.llm_agent import Agent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types
import os
import json
from typing import Optional
import asyncio

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
