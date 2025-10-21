import ollama
import streamlit as st
from rag_pipeline import ingest_pdfs, get_relevant_docs


def local_llm_generate(prompt):
    response = ollama.chat(model="phi3:mini", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

st.title("🤖 SecuraBot — Offline Network Security Chatbot")
st.sidebar.header("📚 Data Management")

if st.sidebar.button("Ingest PDFs"):
    ingest_pdfs()
    st.sidebar.success("PDFs processed and indexed!")

query = st.text_input("Ask a question about your Network Security course:")

if st.button("Get Answer") and query:
    docs = get_relevant_docs(query)
    context = "\n".join([d.page_content for d in docs])

    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer concisely:"

    output = local_llm_generate(prompt)
    st.markdown("### 🧩 Answer:")
    st.write(output)

