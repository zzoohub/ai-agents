from re import I

from google.adk.agents import Agent

from .prompt import IMAGE_BUILDER_DESCRIPTION, IMAGE_BUILDER_PROMPT
from .tools import generate_images

image_builder_agent = Agent(
    name="ImageBuilderAgent",
    description=IMAGE_BUILDER_DESCRIPTION,
    instruction=IMAGE_BUILDER_PROMPT,
    model="gemini-2.5-flash",
    output_key="image_builder_output",
    tools=[generate_images],
)
