import json
import os
import ollama
from rag_pipeline import get_relevant_docs

CHAT_FILE = "chat_history.json"

# --------------------------
# Chat History Management
# --------------------------
def load_chat_history():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_history(chat_history):
    with open(CHAT_FILE, "w") as f:
        json.dump(chat_history, f)

def delete_chat(index, chat_history):
    """Delete a chat by index and return updated history"""
    if 0 <= index < len(chat_history):
        del chat_history[index]
        save_chat_history(chat_history)
    return chat_history

# --------------------------
# Local LLM Response
# --------------------------
def local_llm_generate(prompt):
    response = ollama.chat(model="phi3:mini", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# --------------------------
# RAG Response + Citation
# --------------------------
def get_bot_response(user_query, current_chat):
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

    # Add citations
    sources = []
    for d in docs:
        src = d.metadata.get("source", "Unknown Source")
        sources.append(src)
    if sources:
        bot_response += "\n\n**Sources:** " + ", ".join(set(sources))

    return bot_response
