from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message
import pandas as pd
from agent.agent import query
from database.database_functions import create_session, delete_session, delete_session_messages, get_all_sessions_from_db, get_default_session_id, load_session_messages

load_dotenv()

st.set_page_config(layout="wide")
st.title("📊 Data Explorer Bot")

if "sessions" not in st.session_state:
    default_session_id = get_default_session_id()
    st.session_state.sessions = {"Default": []}
    if not default_session_id:
        create_session(name="Default")
    else:
        st.session_state.sessions["Default"] = load_session_messages(default_session_id)
if "current" not in st.session_state:
    st.session_state.current = "Default"

all_sessions = get_all_sessions_from_db()
for name in all_sessions:
    if name not in st.session_state.sessions:
        st.session_state.sessions[name] = []

new_name = st.sidebar.text_input("New session name", "")

if st.sidebar.button("➕ Create Session"):
    candidate = new_name.strip()
    if not candidate:
        st.sidebar.error("Enter a non-empty name.")
    elif candidate in st.session_state.sessions:
        st.sidebar.error("That session already exists.")
    else:
        new_session_id = create_session(name=candidate)
        all_sessions[candidate] = new_session_id
        st.session_state.sessions[candidate] = []
        st.session_state.current = candidate
        st.rerun()   # re-render so dropdown updates


if st.sidebar.button("➖ Delete Session"):
    current = st.session_state.current
    if current == "Default":
        st.sidebar.error("Cannot delete the Default session.")
    else:
        session_id = all_sessions[current]
        delete_session(all_sessions[current])                  
        st.session_state.sessions.pop(current)
        all_sessions = get_all_sessions_from_db()
        st.session_state.current = "Default"
        st.rerun()             


def on_session_change():
    name = st.session_state.current
    if name in all_sessions:
        session_id = all_sessions[name]
        st.session_state.sessions[name] = load_session_messages(session_id)

# 4) Session selector
st.sidebar.selectbox(
    "Choose session",
    options=list(st.session_state.sessions.keys()),
    key="current",
    on_change=on_session_change
)

# 5) Diagnostics
st.sidebar.markdown(f"**Active session:** {st.session_state.current}")
st.sidebar.markdown(f"Messages: {len(st.session_state.sessions[st.session_state.current])}")

# File uploader
uploaded = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv","xlsx","json"])
if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    elif uploaded.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded)
    elif uploaded.name.endswith(".json"):
        df = pd.read_json(uploaded)

    st.sidebar.dataframe(df.head())

# Main: chat area
def render_messages():
    for index, (sender, text) in enumerate(st.session_state.sessions[st.session_state.current]):
        print(text)
        if sender == "AI" and text.endswith(".png"):
            message("Here is your image", key=f"ai_img_msg_{index}")
            st.image(text, width=500, clamp=True)
        elif sender == "AI":
            message(str(text), key=f"ai_msg_{index}")
        else:
            message(text, is_user=True, key=f"user_msg_{index}")


if st.button("Clear Chat"):
    session_id = all_sessions[st.session_state.current]
    delete_session_messages(session_id)
    st.session_state.sessions[st.session_state.current] = []
    st.rerun()


prompt = st.text_input("Ask about your data…", key="prompt")
if st.button("Send"):
    if not uploaded:
        st.write("Sorry, but you must upload your data first.")
        st.stop()

    session_id = all_sessions[st.session_state.current]

    st.session_state.sessions[st.session_state.current].append(("User", prompt))
    render_messages()
    result = query(prompt, df, session_id)

    st.session_state.sessions[st.session_state.current].append(("AI", str(result)))
    st.rerun()

render_messages()