import pandas as pd
import uuid
from database.chroma_setup import excel_collection

def clear_excel_collection():
    try:
        existing = excel_collection.get()
        ids = existing.get("ids", [])
        if ids:
            # Delete in small batches to avoid ChromaDB bugs
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i + batch_size]
                try:
                    excel_collection.delete(ids=batch)
                except Exception as e:
                    print(f"Batch delete warning: {e}")
        print("Excel collection cleared")
    except Exception as e:
        print("Clear Excel Error:", e)


def add_excel_to_chroma(uploaded_file):
    uploaded_file.seek(0)
 
    filename = uploaded_file.name
    ext = filename.rsplit(".", 1)[-1].lower()

    # FIX: handle CSV separately
    if ext == "csv":
        df = pd.read_csv(uploaded_file)
        sheets = {"sheet1": df}
    else:
        excel = pd.ExcelFile(uploaded_file)
        sheets = {
            sheet: pd.read_excel(excel, sheet_name=sheet)
            for sheet in excel.sheet_names
        }

    for sheet_name, df in sheets.items():
        table_name = sheet_name.lower().replace(" ", "_")

        metadata = f"""
TABLE NAME: {table_name}
FILE: {filename}
COLUMNS: {', '.join(map(str, df.columns))}
SAMPLE ROWS:
{df.head(5).to_string()}
"""
        doc_id = str(uuid.uuid4())

        print(f"\nAdding sheet '{sheet_name}' from {filename} to Chroma")
        print("Rows:", len(df), "| Columns:", list(df.columns))

        try:
            excel_collection.add(
                documents=[metadata],
                ids=[doc_id],
                metadatas=[{"filename": filename, "table_name": table_name}]
            )
            print(f"Sheet '{sheet_name}' added to ChromaDB successfully")
        except Exception as e:
            print("CHROMA ADD ERROR:", type(e), e)