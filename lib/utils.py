def chunk_text(text, chunk_size, overlap=0):
    """
    Splits text into chunks of a specified size with optional overlap.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): The maximum size of each chunk.
        overlap (int): The number of overlapping characters between chunks.

    Returns:
        list: A list of text chunks.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # Move forward but keep overlap
    
    return chunks
