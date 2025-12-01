from google.adk.agents import Agent

from .prompt import VOICE_GENERATOR_DESCRIPTION, VOICE_GENERATOR_PROMPT
from .tools import generate_narrations

voice_generator_agent = Agent(
    name="VoiceGeneratorAgent",
    description=VOICE_GENERATOR_DESCRIPTION,
    instruction=VOICE_GENERATOR_PROMPT,
    model="gemini-2.5-flash",
    tools=[
        generate_narrations,
    ],
)
