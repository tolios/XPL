import os
import requests
from pypdf import PdfReader
from lib.config import CHUNK_SIZE, EMBEDDING_API_URL, EMBEDDING_MODEL
from lib.db import initialize_chroma_client, get_or_create_collection
import lib.utils
import lib.exception as exception

def extract_text_from_pdf(filepath):
    """
    Extracts text from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file.
        
    Returns:
        str: Extracted text.
    """
    text = ""
    try:
        reader = PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        raise e
    return text

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
    if filepath.lower().endswith(".pdf"):
        text = extract_text_from_pdf(filepath)
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

    if existed:
        raise exception.AlreadyProcessed

    # Chunk text
    text_chunks = lib.utils.chunk_text(text, CHUNK_SIZE)

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
