import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def clear_all_tables():

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    """)

    tables = cursor.fetchall()

    for table in tables:

        table_name = table[0]

        cursor.execute(
            f'DROP TABLE IF EXISTS "{table_name}" CASCADE'
        )

        print(f"Dropped {table_name}")

    conn.commit()
    conn.close()