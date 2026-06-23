# chroma_setup.py — already has client, just make sure it's importable
import chromadb

client = chromadb.PersistentClient(path="./db/brand_new_db")  # client is already here

schema_collection = client.get_or_create_collection("schema_collection")
excel_collection = client.get_or_create_collection("excel_collection")
pdf_collection = client.get_or_create_collection("pdf_collection")