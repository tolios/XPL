from chromadb import PersistentClient, AdminClient
from chromadb.config import Settings
import chromadb
from lib.config import CHROMA_PATH
import time
import os

def initialize_chroma_client(db):
    """
    Initializes the ChromaDB client with the specified settings.

    Returns:
        Client: The initialized ChromaDB client.
    """
    # first the admin client creates the db and tenant if they do not exist
    settings = Settings(is_persistent=True, persist_directory=CHROMA_PATH)
    admin_client = AdminClient(settings=settings)

    try:
        admin_client.get_tenant('xpl')
    except chromadb.errors.NotFoundError:
        admin_client.create_tenant('xpl')

    try:
        admin_client.get_database(db, tenant='xpl')
    except:
        admin_client.create_database(db, tenant='xpl')

    return PersistentClient(path=CHROMA_PATH, database=db, tenant='xpl', settings=settings)

def get_or_create_collection(client, collection_name):
    """
    Retrieves or creates a collection within a database.

    Args:
        client (Client): The ChromaDB client object.
        collection_name (str): The name of the collection.
        embedding_function (callable): The function to generate embeddings.

    Returns:
        Collection: The ChromaDB collection object.
    """
    try: 
        collection = client.get_collection(collection_name)
        existed = True
    except:
        # summary here...
        collection = client.create_collection(
            name=collection_name,
            metadata = {
                "created": str(time.time()),
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,
                "hnsw:search_ef": 100,
                "hnsw:M": 16,                
            }
        )

        existed = False
    return collection, existed

def list_collections(folderpath):
    client = PersistentClient(path=CHROMA_PATH,tenant='xpl', database=os.path.abspath(folderpath))
    return client.list_collections()

# ERROR FIX COMMENTED OUT 
# def delete_database(database_name):
#     """
#     Deletes a database under the 'xpl' tenant.

#     Args:
#         database_name (str): The name of the database to delete.
#     """
#     client = PersistentClient(path=DB_DIR)
#     tenant = client.get_or_create_tenant("xpl")

#     try:
#         tenant.delete_database(database_name)
#         print(f"Database '{database_name}' deleted successfully.")
#     except Exception as e:
#         print(f"Error deleting database '{database_name}': {e}")

def delete_collection(filename):
    """
    Deletes a collection from a specified database.

    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection to delete.
    """
    db = os.path.dirname(os.path.abspath(filename))
    collection_name = os.path.basename(filename)
    client = PersistentClient(path=CHROMA_PATH,tenant='xpl', database=db)

    try:
        client.delete_collection(collection_name)
        print(f"Collection '{collection_name}' deleted successfully from database '{db}'.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")
        raise e

def db_exists_for_file(filename):
    """
    Checks if db exists given a specific file...
    Args:
        finename (str): The file to be processed
    Returns:
        exists (bool): True if the corresponding db exists...
    """
    settings = Settings(is_persistent=True, persist_directory=CHROMA_PATH)
    admin_client = AdminClient(settings=settings)

    db = os.path.dirname(os.path.abspath(filename)) 

    for log in admin_client.list_databases(tenant='xpl'):
        if log['name'] == db:
            return True
    
    return False

def db_exists(folderpath):
    """
    Checks if db exists for a folder
    Args:
        folderpath (str): The folder path
    Returns:
        exists (bool): True if the corresponding db exists...
    """

    settings = Settings(is_persistent=True, persist_directory=CHROMA_PATH)
    admin_client = AdminClient(settings=settings)

    db = os.path.abspath(folderpath) 

    for log in admin_client.list_databases(tenant='xpl'):
        if log['name'] == db:
            return True
    
    return False

def list_dbs():
    """
    Lists dbs existing in defined tenant!
    Returns:
        list_dbs (Sequence[Database])
    """
    
    settings = Settings(is_persistent=True, persist_directory=CHROMA_PATH)
    admin_client = AdminClient(settings=settings)

    return admin_client.list_databases(tenant='xpl')

def is_processed(filename):
    """
    Checks if file has been processed or not

    Args:
        finename (str): The file to be processed
    Returns:
        exists (bool): True if it exists
    """
    db = os.path.dirname(os.path.abspath(filename))
    collection_name = os.path.basename(filename)
    client = PersistentClient(path=CHROMA_PATH,tenant='xpl', database=db)

    collections = client.list_collections()
    
    if collection_name in collections:
        return True

    return False

if __name__ == "__main__":

    client = initialize_chroma_client()
