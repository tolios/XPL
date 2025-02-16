import os
import requests
from lib.config import EMBEDDING_API_URL, EMBEDDING_MODEL, LLM_API_URL, LLM_MODEL
from lib.db import initialize_chroma_client

def search_document(filepath, query_text):
    """
    Searches the document for relevant context using ChromaDB.
    
    Args:
        filepath (str): Path to the document.
        query_text (str): The user query.
    
    Returns:
        str: Retrieved context from the document.
    """
    db = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    client = initialize_chroma_client(db)
    collection = client.get_collection(filename)
    
    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding], n_results=3
    )
    
    return "\n".join(doc for doc in results["documents"][0])

# defiend as well in processor.py - bad practice
def get_embedding(text):
    """
    Generates an embedding for the given text using the local Ollama API.
    
    Args:
        text (str): The text to embed.
    
    Returns:
        list: The embedding vector.
    """
    response = requests.post(
        EMBEDDING_API_URL,
        json={"model": EMBEDDING_MODEL, "prompt": text}
    )
    response.raise_for_status()
    return response.json().get("embedding", [])

def answer_question(filepath, question):
    """
    Answers a question based on the document's content using the LLM.
    
    Args:
        filepath (str): Path to the document.
        question (str): The question to answer.
    
    Returns:
        str: AI-generated response.
    """
    context = search_document(filepath, question)
    prompt = f"Document Context:\n{context}\n\nUser Question: {question}\nAnswer:"

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(
        LLM_API_URL,
        headers=headers,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    
    return response.json().get("response", "No response generated.")
