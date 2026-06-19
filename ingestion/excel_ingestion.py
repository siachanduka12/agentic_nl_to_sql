import pandas as pd
import uuid
import os

from database.chroma_setup import excel_collection

def clear_excel_collection():

    try:

        existing = excel_collection.get()

        if existing and existing["ids"]:

            excel_collection.delete(
                ids=existing["ids"]
            )

    except Exception as e:

        print("Clear Excel Error:")
        print(e)

    print("Excel collection cleared")


def add_excel_to_chroma(file_path):

    df = pd.read_excel(file_path)

    table_name = os.path.splitext(
        os.path.basename(file_path)
    )[0].lower()

    metadata = f"""
TABLE NAME:
{table_name}

FILE:
{os.path.basename(file_path)}

COLUMNS:
{', '.join(df.columns)}

SAMPLE ROWS:
{df.head(5).to_string()}
"""

    doc_id = str(uuid.uuid4())
    print("Reading Excel:", file_path)

    print("Rows:", len(df))
    print("Columns:", list(df.columns))

    print("Adding to Chroma...")

    try:

        excel_collection.add(
            documents=[metadata],
            ids=[doc_id],
            metadatas=[
                {
                    "filename": os.path.basename(file_path)
                }
            ]
        )

        print("Added to Chroma successfully")

    except Exception as e:

        print("\n====================")
        print("CHROMA ADD ERROR")
        print("====================")
        print(type(e))
        print(e)

    print(f"{file_path} added to ChromaDB")


def add_excel_folder_to_chroma(folder_path):

    for file in os.listdir(folder_path):

        if file.endswith(".xlsx"):

            full_path = os.path.join(
                folder_path,
                file
            )

            add_excel_to_chroma(
                full_path
            )