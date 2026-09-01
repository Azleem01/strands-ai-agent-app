"""Streamlit chat frontend for the Strands multi-agent Personal Assistant.

Run locally:
    streamlit run app.py

Credentials:
- OPENROUTER_API_KEY is read from `.env` (used by the Search agent).
- AWS credentials for the Bedrock-backed agents (Calendar, Code) come from your
  standard AWS config, e.g. after `aws configure`.
"""

import os

import streamlit as st
from dotenv import load_dotenv

# Load local .env before importing the agents: the agent modules validate their
# API keys at import time, so the environment must be populated first.
load_dotenv()

# On Streamlit Community Cloud there is no .env; mirror st.secrets into the
# environment so the same agent code finds its keys. Guarded so it is a no-op
# locally when no secrets file exists.
try:
    for _key, _value in st.secrets.items():
        if isinstance(_value, str):
            os.environ.setdefault(_key, _value)
except Exception:
    pass

st.set_page_config(
    page_title="Personal assistant",
    page_icon=":material/smart_toy:",
    layout="centered",
)


@st.cache_resource(show_spinner="Starting the personal assistant...")
def load_agent():
    """Build the multi-agent orchestrator once and reuse it across reruns.

    Imported lazily so any missing-credential errors surface in the UI instead
    of crashing the whole script on load.
    """
    from personal_assistant import personal_assistant_agent

    return personal_assistant_agent


# --- Render fast UI first (title, sidebar), slow agent work last ---
st.title(":material/smart_toy: Personal assistant")
st.caption("A multi-agent assistant built with Strands — calendar, coding, and web search.")

with st.sidebar:
    st.subheader("What I can do")
    st.markdown(
        "- :material/event: **Calendar** — create, list, and update appointments\n"
        "- :material/code: **Code** — write and edit files, keep a journal\n"
        "- :material/travel_explore: **Search** — answer general and research questions\n"
    )
    st.caption("Each message is routed to the right specialist automatically.")
    if st.button("Clear conversation", icon=":material/delete:", width="stretch"):
        st.session_state.messages = []
        # Also reset the agent's own conversation memory, not just the display.
        try:
            load_agent().messages.clear()
        except Exception:
            pass
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Build (or reuse) the agent; surface setup problems clearly instead of crashing.
try:
    agent = load_agent()
except Exception as exc:  # noqa: BLE001 - show any startup error to the user
    st.error(f"Couldn't start the assistant: {exc}")
    st.info(
        "Check that `OPENROUTER_API_KEY` is set in your `.env` (Search agent) and "
        "that your AWS credentials are configured via `aws configure` (Bedrock agents)."
    )
    st.stop()

# Replay the conversation so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Onboarding suggestions — shown only on an empty chat, then they disappear.
SUGGESTIONS = {
    ":blue[:material/event:] Today's agenda": "What's on my agenda for today?",
    ":green[:material/event_available:] Book a meeting": (
        "Book a dentist appointment tomorrow at 2pm at the downtown clinic."
    ),
    ":orange[:material/travel_explore:] Ask a question": "What is the Strands Agents SDK?",
}

prompt = st.chat_input("Message your assistant...", submit_mode="disable")

if prompt is None and not st.session_state.messages:
    picked = st.pills("Try asking", options=list(SUGGESTIONS.keys()), label_visibility="collapsed")
    if picked:
        prompt = SUGGESTIONS[picked]

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/smart_toy:"):
        with st.spinner("Thinking..."):
            try:
                answer = str(agent(prompt))
            except Exception as exc:  # noqa: BLE001 - keep the app alive on errors
                answer = f":red[Something went wrong:] {exc}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
