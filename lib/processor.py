import os
import requests
from markitdown import MarkItDown
from lib.config import CHUNK_SIZE, OVERLAP, EMBEDDING_API_URL, EMBEDDING_MODEL
from lib.db import initialize_chroma_client, get_or_create_collection
from lib.summary import get_summary
import lib.utils
import lib.exception as exception

def extract_markdown(filepath):
    """
    Extracts text from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        str: Extracted text.
    """
    try:
        md = MarkItDown()
        doc = md.convert(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        raise e
    return doc.text_content

def generate_embeddings(text_chunks):
    """
    Generates embeddings for a list of text chunks using the local Ollama API.
    
    Args:
        text_chunks (list): List of text strings.
        
    Returns:
        list: List of embeddings.
    """
    embeddings = []
    for chunk in text_chunks:
        try:
            response = requests.post(
                EMBEDDING_API_URL,
                json={"model": EMBEDDING_MODEL, "prompt": chunk}
            )
            response.raise_for_status()
            embedding = response.json().get("embedding")
            if embedding:
                embeddings.append(embedding)
        except requests.RequestException as e:
            print(f"Error generating embedding: {e}")
            raise e
    return embeddings

def process_document(filepath):
    """
    Processes a document: extracts text, generates embeddings, and stores them in the vector database.
    
    Args:
        filepath (str): Path to the document.
    """
    if not os.path.isfile(filepath):
        print(f"File {filepath} does not exist.")
        raise exception.FileNotFoundError

    # Extract text based on file type
    if filepath.lower().endswith(".pdf"): #needs to include all allowed markitdown files
        text = extract_markdown(filepath) 
    else:
        print(f"Unsupported file format: {filepath}")
        raise exception.UnsupportedFileTypeError
    
    if not text:
        print(f"No text extracted from {filepath}.")
        raise exception.ProcessingError
    
    # Spin up a client and find collection
    client = initialize_chroma_client(os.path.dirname(os.path.abspath(filepath)))

    # embedding the file
    collection, existed = get_or_create_collection(client, os.path.basename(filepath))

    if not existed:
        # getnadd summary
        summary = get_summary(text)
        collection.modify(metadata={'summary': summary})

    if existed:
        raise exception.AlreadyProcessed

    # Chunk text
    text_chunks = lib.utils.chunk_text(text, CHUNK_SIZE, overlap=OVERLAP)

    # Generate embeddings
    embeddings = generate_embeddings(text_chunks)

    if not embeddings:
        print("No embeddings generated.")
        return
    
    collection.add(
        documents=text_chunks,
        embeddings=embeddings,
        ids=[str(hash(chunk)) for chunk in text_chunks]
    )
