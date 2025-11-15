import asyncio

import streamlit as st
from agents import Agent, Runner, SQLiteSession

if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history", "chatgpt-clone-memory-db"
    )

session = st.session_state["session"]
with st.sidebar:
    reset = st.button("Reset")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))

prompt = st.chat_input("Write a message for your assistant")

if prompt:
    with st.chat_message("human"):
        st.write(prompt)
