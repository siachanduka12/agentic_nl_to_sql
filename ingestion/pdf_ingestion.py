from pypdf import PdfReader
import uuid

from database.chroma_setup import pdf_collection

def clear_pdf_collection():

    existing = pdf_collection.get()

    if existing["ids"]:
        pdf_collection.delete(ids=existing["ids"])

    print("PDF collection cleared")

def add_pdf_to_chroma(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    metadata = f"""
FILE: {file_path}

PDF CONTENT:

{text}
"""

    doc_id = str(uuid.uuid4())

    pdf_collection.add(
        documents=[metadata],
        ids=[doc_id],
        metadatas=[
            {
                "filename": file_path.split("\\")[-1]
            }
        ]
    )

    print(
        f"{file_path} added to ChromaDB"
    )