import asyncio

import dotenv
import streamlit as st
from agents import Agent, Runner, SQLiteSession

dotenv.load_dotenv()

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful assistant.
        """,
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
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                if message["type"] == "message":
                    st.write(message["content"][0]["text"])


asyncio.run(paint_history())


async def run_agent(message: str):
    with st.chat_message("ai"):
        text_placeholder = st.empty()
        response = ""
        stream = Runner.run_streamed(agent, message, session=session)
        async for event in stream.stream_events():
            if event.type == "raw_response_event":
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
