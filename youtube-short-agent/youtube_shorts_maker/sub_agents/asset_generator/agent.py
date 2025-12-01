from google.adk.agents import ParallelAgent

from .image_generator.agent import image_generator_agent
from .prompt import ASSET_GENERATOR_DESCRIPTION

asset_generator_agent = ParallelAgent(
    name="AssetGeneratorAgent",
    description=ASSET_GENERATOR_DESCRIPTION,
    sub_agents=[
        image_generator_agent,
    ],
)
