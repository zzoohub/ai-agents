from google.adk.agents import SequentialAgent

from .image_builder.agent import image_builder_agent
from .prompt_builder.agent import prompt_builder_agent

image_generator_agent = SequentialAgent(
    name="ImageGeneratorAgent",
    sub_agents=[prompt_builder_agent, image_builder_agent],
)
