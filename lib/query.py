import os
import requests
from lib.config import EMBEDDING_API_URL, EMBEDDING_MODEL, LLM_API_URL, LLM_MODEL, N_DOCS, ALPHA, BM25_PATH
from lib.db import initialize_chroma_client
from lib.bm25 import BM25Retriever
import numpy as np

def min_max_normalize(arr):
    """
    Normalize a NumPy array to the range [0, 1] using Min-Max normalization.
    
    Args:
        arr (np.ndarray): Input array of values.
    
    Returns:
        np.ndarray: Normalized array with values between [0, 1].
    """
    arr = np.array(arr, dtype=np.float64)  # Ensure it's a NumPy array
    min_val, max_val = np.min(arr), np.max(arr)
    
    # Avoid division by zero if all values are the same
    if max_val == min_val:
        return np.zeros_like(arr)  # Return all zeros (or could return ones)
    
    return (arr - min_val) / (max_val - min_val)

def search_document(filepath, query_text):
    """
    Searches the document for relevant context using ChromaDB.
    
    Args:
        filepath (str): Path to the document.
        query_text (str): The user query.
    
    Returns:
        (Context, summary) (str, str): Retrieved context and summary from the document.
    """
    db = os.path.dirname(os.path.abspath(filepath))
    filename = os.path.basename(filepath)
    client = initialize_chroma_client(db)
    collection = client.get_collection(filename)

    query_embedding = get_embedding(query_text)
    results = collection.query(
        query_embeddings=[query_embedding], n_results=N_DOCS,
    )

    test = collection.query(
        query_embeddings=[query_embedding], n_results=collection.count(), include=["distances"]
    )

    print(test["ids"][:N_DOCS])

    ids = np.array([int(i) for i in test["ids"][0]]) # get ids list (its sorted by score)
    dists = np.array(test["distances"][0]) # sorted distances
    #unsort to rerank
    scores_semantic = min_max_normalize((1 - dists[np.argsort(ids)])) # get (1 - 1 - cosine) (to get max)
    bm25R = BM25Retriever.load_json(file_path=os.path.abspath(filepath))
    scores_bm25 = min_max_normalize(np.array(bm25R.score_query(query_text)))

    hybrid_scores = ALPHA * scores_bm25 + (1 - ALPHA) * scores_semantic
    ids = [str(i) for i in np.argsort(-hybrid_scores).tolist()[:N_DOCS]]

    results = collection.get(ids=ids)
    print(ids)
    print(results)

    return "".join(f"{i+1}. "+doc+"\n" for i, doc in enumerate(results["documents"])), collection.metadata.get("summary", "no summary generated")

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
    context, summary = search_document(filepath, question)

    prompt = f'''
    You are a chatbot tasked with answering the user question about a document given
    the document contexts of the document, as well as the provided summary.
    The summary: \n{summary} \nThe contexts: \n{context} \nUser Question: {question}\n

    Generate a json with the following structure:
    {
        "answer" "The answer to the question asked by the user"
    }

    '''
 
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(
        LLM_API_URL,
        headers=headers,
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_ctx": 10000
        }}
    )
    response.raise_for_status()
    
    return response.json().get("response", "No response generated.")
