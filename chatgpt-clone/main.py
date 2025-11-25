import asyncio
from turtle import update

import dotenv
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool

dotenv.load_dotenv()

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful assistant.

        You have access to the following tools:
        - WebSearchTool: Use this when the user asks a question that is not in your training data. Use this to learn about current events.
        """,
        tools=[WebSearchTool()],
    )

agent = st.session_state["agent"]

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history", "chatgpt-clone-memory-db"
    )

session = st.session_state["session"]


async def paint_history():
    messages = await session.get_items()
    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])

        if "type" in message and message["type"] == "web_search_call":
            with st.chat_message("ai"):
                st.write("🔎 Web search in progress..")


asyncio.run(paint_history())


def update_status(status_container, event):
    status_message = {
        "response.web_search_call.completed": ("✅ Web search completed", "complete"),
        "response.web_search_call.in_progress": (
            "🔎 Starting web search",
            "running",
        ),
        "response.web_search_call.searching": (
            "🔎 Web search in progress..",
            "running",
        ),
        "response.completed": (
            "",
            "complete",
        ),
    }

    if event in status_message:
        label, state = status_message[event]
        status_container.update(label=label, state=state)


async def run_agent(message: str):
    with st.chat_message("ai"):
        status_container = st.status("Loading...", expanded=False)
        text_placeholder = st.empty()
        response = ""
        stream = Runner.run_streamed(agent, message, session=session)

        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)


prompt = st.chat_input("Write a message for your assistant")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
    asyncio.run(run_agent(prompt))

with st.sidebar:
    reset = st.button("Reset")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
