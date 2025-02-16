import os
import toml

# Define the path to the configuration file
CONFIG_FILE_PATH = os.path.dirname(__file__)+'/../config.toml'

# Load the configuration file
with open(CONFIG_FILE_PATH, 'r') as config_file:
    config = toml.load(config_file)

# Accessing the configurations
EMBEDDING_MODEL = config['embedding_model']['name']
EMBEDDING_API_URL = config['embedding_model']['api_url']

LLM_MODEL = config['llm_model']['name']
LLM_API_URL = config['llm_model']['api_url']

CHUNK_SIZE = config['document_processing']['chunk_size']
CHROMA_PATH = config['document_processing']['chroma_path']

LOGGING_LEVEL = config['logging']['level']
