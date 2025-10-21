import streamlit as st
from rag_pipeline import get_relevant_docs
import ollama
from time import sleep
import json
import os


CHAT_HISTORY_FILE = "chat_history.json"

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# --------------------------
# Local LLM function
# --------------------------
def local_llm_generate(prompt):
    response = ollama.chat(model="phi3:mini", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="SecuraBot", layout="wide")

# --------------------------
# Initialize session state
# --------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = load_chat_history()

if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = 0

if "temp_input" not in st.session_state:
    st.session_state["temp_input"] = ""  # for clearing text box

# --------------------------
# Sidebar
# --------------------------
with st.sidebar:
    st.header("💬 Chats")

    if st.button("+ New Chat"):
        st.session_state["chat_history"].append({"messages": []})
        st.session_state["selected_chat"] = len(st.session_state["chat_history"]) - 1
        save_chat_history(st.session_state["chat_history"])

    for i, chat in enumerate(st.session_state["chat_history"]):
        label = f"Chat {i + 1}"
        if st.button(label, key=f"chat_{i}"):
            st.session_state["selected_chat"] = i

# --------------------------
# Ensure at least one chat exists
# --------------------------
if len(st.session_state["chat_history"]) == 0:
    st.session_state["chat_history"].append({"messages": []})
    st.session_state["selected_chat"] = 0

current_chat = st.session_state["chat_history"][st.session_state["selected_chat"]]

# --------------------------
# Chat display
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
# Message input (Form for better UX)
# --------------------------
with st.form(key="chat_form", clear_on_submit=True):
    query = st.text_input(
        "Message SecuraBot...",
        key="input_box",
        placeholder="Type your question here...",
    )
    send = st.form_submit_button("Send")

# --------------------------
# Send message handling
# --------------------------
if send and query.strip():
    # Add user's message immediately
    current_chat["messages"].append({"user": query, "bot": "⏳ Generating response..."})
    st.session_state["temp_input"] = ""  # Clear input

    # Refresh chat to show "Generating response..."
    st.rerun()

# Detect if last message is pending response
if current_chat["messages"] and current_chat["messages"][-1]["bot"] == "⏳ Generating response...":
    user_query = current_chat["messages"][-1]["user"]

    with st.spinner("🤖 Generating response..."):
        try:
            # RAG retrieval
            docs = get_relevant_docs(user_query)
            context = "\n".join([d.page_content for d in docs])

            # Build prompt with chat history
            conversation_context = ""
            for msg in current_chat["messages"][:-1]:
                conversation_context += f"User: {msg['user']}\nBot: {msg['bot']}\n"

            prompt = (
                f"{conversation_context}\nContext:\n{context}\n\n"
                f"User Question: {user_query}\nAnswer concisely:"
            )

            # Generate LLM response
            bot_response = local_llm_generate(prompt)

            # Update the last pending message
            current_chat["messages"][-1]["bot"] = bot_response
            save_chat_history(st.session_state["chat_history"])

                        # --- 📚 Add Source Citations Below ---
            if docs:
                citation_text = "\n\n**📘 Sources used:**\n"
                sources = set()

                for d in docs:
                    source_name = d.metadata.get("source", "Unknown document")
                    page_num = d.metadata.get("page", None)

                    if page_num:
                        sources.add(f"{source_name} (Page {page_num})")
                    else:
                        sources.add(source_name)

                for s in sources:
                    citation_text += f"- {s}\n"

                # Append citations to the bot's response
                current_chat["messages"][-1]["bot"] += citation_text
            else:
                current_chat["messages"][-1]["bot"] += "\n\n_No citation data available._"

        except Exception as e:
            current_chat["messages"][-1]["bot"] = f"⚠️ Error: {e}"

    # Refresh to show bot’s reply
    st.rerun()
