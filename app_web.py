# app_web.py
# TAM - Team Activity Monitor
# Streamlit web interface

import streamlit as st
from app import handle_query
from config.config import USE_MOCK_DATA, NAME_EXTRACTION_MODE

# --- page config ---
st.set_page_config(
    page_title="TAM — Team Activity Monitor",
    page_icon="🔍",
    layout="centered"
)

# --- sidebar ---
with st.sidebar:
    st.title("⚙️ TAM Config")
    st.divider()

    # data mode
    st.subheader("Data Mode")
    if USE_MOCK_DATA:
        st.success("Mock Data (Demo Mode)")
    else:
        st.info("Live APIs (Production Mode)")

    # extraction mode
    st.subheader("Name Extraction")
    if NAME_EXTRACTION_MODE == "advanced":
        st.success("Advanced (Regex + spaCy + OpenAI)")
    else:
        st.info("Basic (Regex + spaCy)")

    st.divider()

    # team members
    st.subheader("👥 Team Members")
    try:
        import json
        with open("data/members.json") as f:
            members = json.load(f)
        for member in members:
            st.markdown(f"- {member['name']}")
    except FileNotFoundError:
        st.warning("members.json not found. Run scripts/generate_mock_data.py first.")

    st.divider()

    # example queries
    st.subheader("💡 Example Queries")
    examples = [
        "What is John working on?",
        "Show me recent activity for Priya",
        "What has Ravi been working on?",
        "Show me Lisa's pull requests",
        "What tickets is Arjun working on?",
    ]
    for example in examples:
        st.code(example, language=None)

    st.divider()

    # clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- header ---
st.title("🔍 TAM — Team Activity Monitor")
st.caption("Ask me what any team member is working on across JIRA and GitHub.")
st.divider()

# --- initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- welcome message ---
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hi! I'm TAM, your **Team Activity Monitor**.\n\n"
            "Ask me what any team member is working on and I'll pull their "
            "latest activity from JIRA and GitHub.\n\n"
            "Try something like: *What is John working on?*"
        )

# --- render chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- chat input ---
if prompt := st.chat_input("What is John working on?"):

    # display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # handle special commands
    if prompt.strip().lower() == "exit":
        response = "To exit TAM, simply close this browser tab."
    elif prompt.strip().lower() == "help":
        response = (
            "**Example queries:**\n"
            "- What is John working on?\n"
            "- Show me recent activity for Sarah\n"
            "- What has Mike been working on this week?\n"
            "- Show me Lisa's pull requests\n"
            "- What tickets is Arjun working on?\n\n"
            "You can also check the sidebar for the full list of team members."
        )
    else:
        with st.chat_message("assistant"):
            with st.spinner("Fetching activity data..."):
                response = handle_query(prompt)
            st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        st.stop()

    # display and save response for special commands
    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })