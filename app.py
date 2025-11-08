import streamlit as st
from tutor_agent import tutor_agent_page
from quiz_agent import quiz_agent_page

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="SecuraBot", layout="wide")

# --------------------------
# Sidebar Navigation
# --------------------------
st.sidebar.title("🤖 SecuraBot")
page = st.sidebar.radio("Choose Agent", ["📘 Tutor Agent", "🧠 Quiz Agent"])

# --------------------------
# Page Routing
# --------------------------
if page == "📘 Tutor Agent":
    tutor_agent_page()
#elif page == "🌐 Tutor Agent (Web Search)":
#    tutor_webpage()
#elif page == "Quiz Agent (Web Search)":
#    quiz_agent_web_page()
else:
    quiz_agent_page()
