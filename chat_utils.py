import json
import os
import ollama
from rag_pipeline import get_relevant_docs
from google import genai
from logger_utils import create_log_entry

def get_chat_file(agent_key):
    if "quiz" in agent_key:
        return "chat_history_quiz.json"
    else:
        return "chat_history_tutor.json"


def load_chat_history(agent_key):
    chat_file = get_chat_file(agent_key)
    if os.path.exists(chat_file):
        with open(chat_file, "r") as f:
            return json.load(f)
    return []

def save_chat_history(chat_history, agent_key):
    chat_file = get_chat_file(agent_key)
    with open(chat_file, "w") as f:
        json.dump(chat_history, f, indent=2)

def delete_chat(index, chat_history, agent_key=None):
    if 0 <= index < len(chat_history):
        del chat_history[index]
        if agent_key:
            save_chat_history(chat_history, agent_key)
    return chat_history


client = genai.Client(api_key="AIzaSyA7j45L-0uSipbGCUjAjhtkyIdYjDVXRd0")

def local_llm_generate(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


def get_bot_response(user_query, current_chat):
    docs = get_relevant_docs(user_query)
    context = "\n".join([d.page_content for d in docs])

    conversation_context = ""
    for msg in current_chat["messages"][:-1]:
        conversation_context += f"User: {msg['user']}\nBot: {msg['bot']}\n"

    prompt = (
        f"{conversation_context}\nContext:\n{context}\n\n"
        f"You are a networksecurity tutor. Explain clearly and concisely.\n"
        f"User Question: {user_query}\nAnswer below:\n"
    )

    bot_response = local_llm_generate(prompt)

    sources = []
    for d in docs:
        src = d.metadata.get("source", "Unknown Source")
        sources.append(src)
    if sources:
        bot_response += "\n\n**Sources:** " + ", ".join(set(sources))

    create_log_entry(user_query, docs, bot_response, agent_type="tutor")

    return bot_response


def get_quiz_response(user_query, current_chat):
    docs = get_relevant_docs(user_query)
    context = "\n".join([d.page_content for d in docs])

    conversation_context = ""
    for msg in current_chat["messages"][:-1]:
        conversation_context += f"User: {msg['user']}\nBot: {msg['bot']}\n"

    prompt = f"""
You are a Quiz Agent specialized in Networksecurity.
Context: {context}

If the user says "start quiz on <topic>", create 5 MCQs with 4 options each.
Ask one question at a time.
After each user answer:
- Check if it is correct.
- Respond with feedback ("Correct!" or "Wrong, the right answer is ...").
- Then move to the next question.
Keep a conversational tone.

Conversation so far:
{conversation_context}

User: {user_query}
Respond appropriately as the Quiz Agent:
"""
    bot_response = local_llm_generate(prompt)
    
    create_log_entry(user_query, docs, bot_response, agent_type="quiz")
    
    return bot_response
