import chromadb
from sentence_transformers import SentenceTransformer
from schema_data import SCHEMAS

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
client = chromadb.PersistentClient(path="./db/brand_new_db")

# Delete old collection if it exists
try:
    client.delete_collection("schema_collection")
except:
    pass

# Create fresh collection
collection = client.create_collection(
    name="schema_collection"
)

print("Loading schemas into ChromaDB...")

for i, schema in enumerate(SCHEMAS):

    embedding = model.encode(schema).tolist()

    collection.add(
        ids=[str(i)],
        documents=[schema],
        embeddings=[embedding]
    )

print("Total documents:", collection.count())
print("Schema loaded successfully!")