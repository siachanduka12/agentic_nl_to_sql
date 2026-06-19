import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()


def excel_to_postgres(excel_file):

    from sqlalchemy.engine import URL

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )

    engine = create_engine(url)

    excel = pd.ExcelFile(excel_file)

    print("\nSheets Found:")
    print(excel.sheet_names)

    for sheet in excel.sheet_names:

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet
        )

        df.columns = [
            col.lower()
            .replace(" ", "_")
            for col in df.columns
        ]

        table_name = (
        sheet.lower()
        .replace(" ", "_")
    )

        df.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False
        )

        print(
            f"Created table: {table_name}"
        )

    print(
        "\nExcel imported successfully!"
    )