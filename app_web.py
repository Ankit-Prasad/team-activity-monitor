# app_web.py
# TAM - Team Activity Monitor
# Streamlit web interface

import streamlit as st
from app import fetch_all_data, handle_query

# --- page config ---
st.set_page_config(
    page_title="TAM — Team Activity Monitor",
    page_icon="🔍",
    layout="centered"
)

# --- header ---
st.title("🔍 TAM — Team Activity Monitor")
st.caption("Ask me what any team member is working on.")

# --- initialize chat history in session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- render existing chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- chat input ---
if prompt := st.chat_input("What is John working on?"):

    # display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # save user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # handle special commands
    if prompt.strip().lower() == "exit":
        response = "To exit, simply close this browser tab."
    elif prompt.strip().lower() == "help":
        response = """
**Example queries:**
- What is John working on?
- Show me recent activity for Sarah
- What has Mike been working on this week?
- Show me Lisa's pull requests
- What tickets is Alex working on?
        """
    else:
        # generate response
        with st.spinner("Fetching activity data..."):
            response = handle_query(prompt)

    # display and save assistant response
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })