import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import os

load_dotenv()


def excel_to_postgres(excel_file):
    excel_file.seek(0)
    filename = excel_file.name
    ext = filename.rsplit(".", 1)[-1].lower()

    print(f"\nProcessing file: {filename}")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )
    engine = create_engine(url)

    if ext == "csv":
        df = pd.read_csv(excel_file)
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        table_name = filename.rsplit(".", 1)[0].lower().replace(" ", "_")
        print(f"Creating table: {table_name} | Rows: {len(df)}")
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Created table: {table_name}")
    else:
        excel = pd.ExcelFile(excel_file)
        print("Sheets Found:", excel.sheet_names)

        for sheet in excel.sheet_names:
            df = pd.read_excel(excel, sheet_name=sheet)
            df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
            table_name = sheet.lower().replace(" ", "_")
            print(f"Creating table: {table_name} | Rows: {len(df)}")
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"Created table: {table_name}")

    print("\nFile imported successfully!")