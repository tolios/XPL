import requests
from lib.config import LLM_API_URL, LLM_MODEL, S_CHUNK_SIZE, S_OVERLAP, MAX_SUMMARY_LEN
from lib.utils import chunk_text
import tqdm

def get_summary(md:str):
    # return _get_summary(md)
    return get_rolling_summary(md, chunk_size=S_CHUNK_SIZE, overlap=S_OVERLAP, max_summary_len=MAX_SUMMARY_LEN)

def _get_summary(md: str):
    """
    Generates summary for a given file
    
    Args:
        md (str): markdown content of file
    
    Returns:
        str: AI-generated summary.
    """

    prompt = f'''
    Provide the summary for the following markdown file:
    {md}
    summary:
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
    
    return response.json().get("response", "No summary provided")

def get_joint_summary_input(current_summary, previous_summary, chunk, max_summary_len):
    """
    Generates summary for a given file
    
    Args:
        md (str): markdown content of file
    
    Returns:
        str: AI-generated summary.
    """

    prompt = f"""
        PREVIOUS SUMMARY VERSION:
        {previous_summary}
            
        CURRENT SUMMARY:
        {current_summary}
            
        NEW CONTENT TO INCORPORATE:
        {chunk}
            
        Create an updated summary that:
            1. Maintains approximately {max_summary_len} characters or less
            2. Preserves the core information from the current summary
            3. Remove less important details from the current summary, but with ease so as to not lose global view
            4. Incorporates important new information from the new content
            5. Resolves any contradictions between previous information and new content
            6. Maintains a coherent, unified summary that reads as a single document
            
        The summary should converge toward a stable representation of the entire document's key information.
    """
 
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
    
    return response.json().get("response", "No summary provided") 

def get_rolling_summary(md: str, chunk_size=2000, overlap=0, max_summary_len=500):
    """
    Generates summary for a given file using a rolling technique to deal with the large size
    
    Args:
        md (str): markdown content of file
    
    Returns:
        str: AI-generated summary.
    """
    print(chunk_size, overlap, max_summary_len)

    chunks = chunk_text(md, chunk_size, overlap)

    current_summary = ""
    previous_summary = ""

    i = 0
    for chunk in tqdm.tqdm(chunks):
        if i == 0:
            current_summary = _get_summary(chunk)
            i += 1
        else:
            summary = get_joint_summary_input(current_summary, previous_summary, chunk, max_summary_len)
            previous_summary = current_summary
            current_summary = summary
            i += 1

        print("########", i, current_summary)
    
    return current_summary
