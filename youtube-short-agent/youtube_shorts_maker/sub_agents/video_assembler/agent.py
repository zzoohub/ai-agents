from google.adk.agents import Agent

from .prompt import VIDEO_ASSEMBLER_DESCRIPTION, VIDEO_ASSEMBLER_PROMPT
from .tools import assemble_video

video_assembler_agent = Agent(
    name="VideoAssemblerAgent",
    model="gemini-2.5-flash",
    description=VIDEO_ASSEMBLER_DESCRIPTION,
    instruction=VIDEO_ASSEMBLER_PROMPT,
    output_key="video_assembler_output",
    tools=[
        assemble_video,
    ],
)
