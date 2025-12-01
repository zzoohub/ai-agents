from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .prompt import SHORTS_PRODUCER_DESCRIPTION, SHORTS_PRODUCER_PROMPT
from .sub_agents.asset_generator.agent import asset_generator_agent
from .sub_agents.content_planner.agent import content_planner_agent

shorts_producer_agent = Agent(
    name="ShortsProducerAgent",
    description=SHORTS_PRODUCER_DESCRIPTION,
    instruction=SHORTS_PRODUCER_PROMPT,
    model="gemini-2.5-flash",
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=asset_generator_agent),
    ],
)


root_agent = shorts_producer_agent
