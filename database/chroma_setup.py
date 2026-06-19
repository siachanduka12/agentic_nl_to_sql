import chromadb

client = chromadb.PersistentClient(
    path="./db/brand_new_db"
)

schema_collection = client.get_or_create_collection(
    "schema_collection"
)

excel_collection = client.get_or_create_collection(
    "excel_collection"
)

pdf_collection = client.get_or_create_collection(
    "pdf_collection"
)