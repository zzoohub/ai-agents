from typing import List

from google.adk.agents import Agent
from pydantic import BaseModel, Field

from .prompt import PROMPT_BUILDER_DESCRIPTION, PROMPT_BUILDER_PROMPT


class OptimizedPrompt(BaseModel):
    scene_id: int = Field()
    optimized_prompt: str


class PromptBuilderOutput(BaseModel):
    optimized_prompts: List[OptimizedPrompt]


prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    description=PROMPT_BUILDER_DESCRIPTION,
    instruction=PROMPT_BUILDER_PROMPT,
    output_schema=PromptBuilderOutput,
    model="gemini-2.5-flash-lite",
    output_key="prmopt_builder_output",
)
