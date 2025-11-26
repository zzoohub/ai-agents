import asyncio
from turtle import up

import dotenv
import streamlit as st
from agents import Agent, FileSearchTool, Runner, SQLiteSession, WebSearchTool
from openai import OpenAI

client = OpenAI()

dotenv.load_dotenv()

VECTOR_STORE_ID = "vs_6926b2fb3c6c8191958445e0430dedcc"

if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="ChatGPT Clone",
        instructions="""
        You are a helpful assistant.
        You have access to the following tools:
        - WebSearchTool: Use this when the user asks a question that is not in your training data. Use this to learn about current or future events.
        - FileSearchTool: Use this when the user asks a question about facts related to themselves. or when they ask questions about specific files.
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(vector_store_ids=[VECTOR_STORE_ID], max_num_results=3),
        ],
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

        if "type" in message:
            if message["type"] == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔎 Web search in progress..")

            elif message["type"] == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🔎 File search in progress..")


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
        "response.file_search_call.completed": ("✅ File search completed", "complete"),
        "response.file_search_call.in_progress": (
            "🔎 Starting file search",
            "running",
        ),
        "response.file_search_call.searching": (
            "🔎 File search in progress..",
            "running",
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


prompt = st.chat_input(
    "Write a message for your assistant", accept_file=True, file_type=["txt"]
)

if prompt:
    for file in prompt.files:
        if file.type.startswith("text/"):
            with st.chat_message("ai"):
                with st.status("Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()), purpose="user_data"
                    )
                    status.update(label="Attaching file...")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID, file_id=uploaded_file.id
                    )
                    status.update(label="File uploaded", state="complete")

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    reset = st.button("Reset")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
