import streamlit as st
from chat_utils import load_chat_history, save_chat_history, delete_chat, get_bot_response

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="SecuraBot", layout="wide")

# --------------------------
# Initialize Session State
# --------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = load_chat_history()

if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = 0

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("💬 Chats")

    # Create new chat
    if st.button("+ New Chat"):
        st.session_state["chat_history"].append({"messages": []})
        st.session_state["selected_chat"] = len(st.session_state["chat_history"]) - 1
        save_chat_history(st.session_state["chat_history"])

    # Display chat list
    for i, chat in enumerate(st.session_state["chat_history"]):
        cols = st.columns([3, 1])
        with cols[0]:
            if st.button(f"Chat {i + 1}", key=f"chat_{i}"):
                st.session_state["selected_chat"] = i
        with cols[1]:
            if st.button("🔥", key=f"del_{i}"):
                st.session_state["chat_history"] = delete_chat(i, st.session_state["chat_history"])
                st.session_state["selected_chat"] = 0
                st.rerun()

# Ensure at least one chat exists
if len(st.session_state["chat_history"]) == 0:
    st.session_state["chat_history"].append({"messages": []})
    st.session_state["selected_chat"] = 0

current_chat = st.session_state["chat_history"][st.session_state["selected_chat"]]

# --------------------------
# Chat Display
# --------------------------
st.subheader("🤖 SecuraBot")

chat_container = st.container()
with chat_container:
    if not current_chat["messages"]:
        st.info("Start chatting with SecuraBot 👇")
    for msg in current_chat["messages"]:
        st.markdown(f"**🧑 You:** {msg['user']}") 
        st.markdown(f"**🤖 SecuraBot:** {msg['bot']}")
        st.divider()

# --------------------------
# Message Input (Form)
# --------------------------
with st.form(key="chat_form", clear_on_submit=True):
    query = st.text_input(
        "Message SecuraBot...",
        key="input_box",
        placeholder="Type your question here...",
    )
    send = st.form_submit_button("Send")

# --------------------------
# Message Handling
# --------------------------
if send and query.strip():
    current_chat["messages"].append({"user": query, "bot": "⏳ Generating response..."})
    save_chat_history(st.session_state["chat_history"])
    st.rerun()

# Detect pending message
if current_chat["messages"] and current_chat["messages"][-1]["bot"] == "⏳ Generating response...":
    user_query = current_chat["messages"][-1]["user"]

    with st.spinner("🤖 Generating response..."):
        try:
            bot_response = get_bot_response(user_query, current_chat)
            current_chat["messages"][-1]["bot"] = bot_response
            save_chat_history(st.session_state["chat_history"])
        except Exception as e:
            current_chat["messages"][-1]["bot"] = f"⚠️ Error: {e}"
            save_chat_history(st.session_state["chat_history"])

    st.rerun()
