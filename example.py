from chromadb import PersistentClient, AdminClient
from chromadb.config import Settings

# Define the path to your persistent storage
CHROMA_PATH = '.xplchroma'


# first the admin client creates the db and tenant if they do not exist
settings = Settings(is_persistent=True, persist_directory=CHROMA_PATH)
admin_client = AdminClient(settings=settings)

db = admin_client.list_databases(tenant='xpl')[1]['name']

# Initialize the ChromaDB client with persistent settings
client = PersistentClient(path=CHROMA_PATH,tenant='xpl', database=db)
# # Replace 'your_collection_name' with the actual name of your collection
# collection_name = 'cl_anthropic.pdf'
# collection = client.get_collection(collection_name)

# # Fetch all items in the collection
# data = collection.get()


# # Display the retrieved data
# print("IDs:", data['ids'])
# print("Documents:", data['documents'])
# print("Metadata:", data['metadatas'])

print(client.list_collections())
