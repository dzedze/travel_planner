from google.genai import Client
from google.adk.agents.llm_agent import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.tools.example_tool import ExampleTool
from google.genai import types
import os
import json
from typing import Optional