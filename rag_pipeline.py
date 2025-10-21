import os
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Paths
PDF_DIR = "data/pdfs"
DB_DIR = "data/chroma_db"

def ingest_pdfs():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []

    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(PDF_DIR, file))
            docs = loader.load_and_split(text_splitter)
            documents.extend(docs)

    vectordb = Chroma.from_documents(documents, embedding=embeddings, persist_directory=DB_DIR)
    vectordb.persist()
    print("✅ PDF data ingested successfully!")
    return vectordb


def get_relevant_docs(query):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    results = vectordb.similarity_search(query, k=4)
    return results
