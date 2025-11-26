import asyncio
import base64

import dotenv
import streamlit as st
from agents import (
    Agent,
    FileSearchTool,
    ImageGenerationTool,
    Runner,
    SQLiteSession,
    WebSearchTool,
)
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

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
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "low",
                    "output_format": "jpeg",
                    "moderation": "low",
                    "partial_images": 1,
                }
            ),
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
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])

                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"])

        if "type" in message:
            message_type = message["type"]

            if message_type == "web_search_call":
                with st.chat_message("ai"):
                    st.write("🔎 Web search in progress..")

            elif message_type == "file_search_call":
                with st.chat_message("ai"):
                    st.write("🔎 File search in progress..")
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)


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
        "response.image_generation_call.in_progress": (
            "✅ Drawing image...",
            "running",
        ),
        "response.image_generation_call.generating": (
            "✅ Drawing image...",
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
        image_placeholder = st.empty()
        response = ""
        stream = Runner.run_streamed(agent, message, session=session)

        async for event in stream.stream_events():
            if event.type == "raw_response_event":
                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response)

                elif event.data.type == "response.image_generation_call.partial_image":
                    image = base64.b64decode(event.data.partial_image_b64)
                    image_placeholder.image(image)


prompt = st.chat_input(
    "Write a message for your assistant",
    accept_file=True,
    file_type=["txt", "jpg", "jpeg", "png"],
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
        elif file.type.startswith("image/"):
            with st.status("Uploading image...") as status:
                file_byte = file.getvalue()
                base64_data = base64.b64encode(file_byte).decode("utf-8")
                data_uri = f"data:{file.type};base64,{base64_data}"
                asyncio.run(
                    session.add_items(
                        [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "input_image",
                                        "detail": "auto",
                                        "image_url": data_uri,
                                    }
                                ],
                            }
                        ]
                    )
                )
                status.update(label="Image uploaded", state="complete")

            with st.chat_message("human"):
                st.image(data_uri)

    if prompt.text:
        with st.chat_message("human"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    reset = st.button("Reset")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
