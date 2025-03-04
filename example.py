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

t = '''# eXPLain

## Overview

`xpl` is a command-line tool that helps you analyze and query documents using AI-powered embeddings and language models. It leverages local AI models for text generation and embeddings, combined with a vector database for efficient searching.

As a cli tool it aims to be used only as such. We do have now tons of implementations that are way better than this. :^)

### Author's note

This tool was/is made because I simply can't keep up with all the crazy developments around the world, and need a machine to lossy-say to me what happens. To not get out of my terminal...

### ATTENTION
For now it only uses ollama models. The aim would be to integrate many possible api's, or
even custom embedding, and llms..chmod +x xpl.

ollama link: https://github.com/ollama/ollama

## Features
- **Process Documents**: Extracts text from ALL [markitdown](https://github.com/microsoft/markitdown) supported formats (the basic ones) and generates embeddings.
- **Query Documents**: Ask questions about a document and get AI-powered responses.
- **Manage Databases**: Store, retrieve, and delete document embeddings from a [ChromaDB](https://www.trychroma.com/) vector database.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/tolios/XPL.git
   cd XPL
   ```
2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```
3. Make the script executable:
   ```sh
   chmod +x xpl
   ```

## Configuration

`xpl` uses a `config.toml` file (TOML format) for configuration. Default settings are in `lib/config.py`. To modify configurations, update the file:
```toml
EMBEDDING_MODEL = "jina/jina-embeddings-v2-small-en"
LLM_MODEL = "deepseek-r1:1.5b"
CHUNK_SIZE = 500
```

## Usage

### Processing a Document
To process a document and store embeddings:
```sh
xpl process example.pdf
```

### Querying a Document
To ask a question about a document:
```sh
xpl ask example.pdf "What is the main topic?"
```

### Listing Databases
To list stored databases in a tabular format:
```sh
xpl dbs
```

### Deleting a Collection
To delete stored embeddings for a document:
```sh
xpl process -d example.pdf
```

## Dependencies
- **Python** 3.12+
- **Poetry** (for package management)
- **pypdf** (for PDF text extraction)
- **requests** (for API calls)
- **ChromaDB** (for vector database storage)
- **Click** (for CLI functionality)
- **Tabulate** (for formatted output)

## Development
To contribute, follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```sh
   git checkout -b feature-branch
   ```
3. Commit changes and push:
   ```sh
   git commit -m "Add new feature"
   git push origin feature-branch
   ```
4. Open a Pull Request.

## License
This project is licensed under the MIT License.

## Author
Created by **Apostolos Kakampakos**. Contributions are welcome!
'''

s = chunk_text(t, 150, 50)
print(s)