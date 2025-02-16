def chunk_text(text, chunk_size):
    """
    Splits text into chunks of a specified size.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): The maximum size of each chunk.

    Returns:
        list: A list of text chunks.
    """
    chunks = []
    words = text.split()  # Preserve words rather than splitting mid-word
    current_chunk = []

    for word in words:
        if sum(len(w) for w in current_chunk) + len(current_chunk) + len(word) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
