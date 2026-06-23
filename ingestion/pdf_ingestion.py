from pypdf import PdfReader
import uuid

from database.chroma_setup import pdf_collection

def clear_pdf_collection():
    try:
        existing = pdf_collection.get()
        ids = existing.get("ids", [])
        if ids:
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i + batch_size]
                try:
                    pdf_collection.delete(ids=batch)
                except Exception as e:
                    print(f"Batch delete warning: {e}")
        print("PDF collection cleared")
    except Exception as e:
        print("Clear PDF Error:", e)


def add_pdf_to_chroma(uploaded_file):

    uploaded_file.seek(0)

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    metadata = f"""
FILE: {uploaded_file.name}

PDF CONTENT:

{text}
"""

    doc_id = str(uuid.uuid4())

    pdf_collection.add(
        documents=[metadata],
        ids=[doc_id],
        metadatas=[
            {
                "filename": uploaded_file.name
            }
        ]
    )

    print(f"{uploaded_file.name} added to ChromaDB")