import psycopg2
from groq import Groq
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import time
from database.chroma_setup import (
    schema_collection,
    excel_collection,
    pdf_collection
)
from utils.logger import log_info, log_error

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel("gemini-2.5-flash")

start = time.time()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model Load Time:", round(time.time() - start, 3), "sec")

start = time.time()
print("Chroma Load Time:", round(time.time() - start, 3), "sec")


def retrieve_context(question):
    query_embedding = embedding_model.encode(question).tolist()

    context = ""
    used_sources = []

    # ── Schema collection (may be empty — guard it) ──────────────────────────
    if schema_collection.count() > 0:
        schema_results = schema_collection.query(
            query_embeddings=[query_embedding],
            n_results=1
        )
        print("\nSchema Distance:", schema_results["distances"])
        if schema_results["documents"][0]:
            context += "\nSCHEMA CONTEXT:\n" + schema_results["documents"][0][0]
            used_sources.append("Schema")
    else:
        print("\n[WARN] schema_collection is empty — skipping schema retrieval")

    # ── Excel collection ──────────────────────────────────────────────────────
    print("\nExcel Count:", excel_collection.count())

    if excel_collection.count() > 0:
        excel_results = excel_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(5, excel_collection.count())
        )
        print("\n===== EXCEL RESULTS =====")
        print(excel_results)
        print("\nExcel Distance:", excel_results["distances"])

        if excel_results["documents"][0]:
            for i, doc in enumerate(excel_results["documents"][0]):
                context += f"\nEXCEL CONTEXT {i+1}:\n" + doc
            for meta in excel_results["metadatas"][0]:
                try:
                    used_sources.append(meta["filename"])
                except Exception:
                    pass
    else:
        print("\n[WARN] excel_collection is empty — skipping excel retrieval")

    # ── PDF collection ────────────────────────────────────────────────────────
    if pdf_collection.count() > 0:
        pdf_results = pdf_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(5, pdf_collection.count())
        )
        print("\nPDF Distance:", pdf_results["distances"])

        if pdf_results["documents"][0]:
            for i, doc in enumerate(pdf_results["documents"][0]):
                context += f"\nPDF CONTEXT {i+1}:\n" + doc
            # FIX: collect ALL pdf filenames, not just last one
            for meta in pdf_results["metadatas"][0]:
                try:
                    used_sources.append(meta["filename"])
                except Exception:
                    used_sources.append("PDF Source")
    else:
        print("\n[WARN] pdf_collection is empty — skipping pdf retrieval")

    print("\n===== USED SOURCES =====", used_sources)
    print("\n===== CONTEXT LENGTH =====", len(context))
    print("\n===== CONTEXT =====\n", context)
    used_sources = list(dict.fromkeys(used_sources))
    return context, used_sources


def validate_sql(sql):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    sql_upper = sql.upper()
    for word in forbidden:
        if word in sql_upper:
            raise Exception(f"Forbidden SQL detected: {word}")
    return True


def generate_sql(prompt):
    try:
        log_info("Using Gemini")
        start = time.time()
        response = gemini_model.generate_content(prompt)
        print("Gemini Time:", round(time.time() - start, 3), "sec")
        return response.text, "Gemini"
    except Exception as e:
        log_error(f"Gemini Failed: {e}")
        log_info("Switching to Groq")
        start = time.time()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        print("Groq Time:", round(time.time() - start, 3), "sec")
        return response.choices[0].message.content, "Groq"


def explain_sql(sql):
    prompt = f"""
    Explain this SQL query in one simple sentence.
    SQL: {sql}
    Rules:
    1. Keep explanation under 20 words.
    2. No technical jargon.
    3. Return only the explanation.
    """
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("\nExplanation Error:", e)
        return "This query retrieves data from the database."


def log_query(question, sql, provider, explanation, total_time):
    with open("query_logs.txt", "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"Question: {question}\n")
        f.write(f"Provider: {provider}\n")
        f.write(f"SQL: {sql}\n")
        f.write(f"Explanation: {explanation}\n")
        f.write(f"Total Time: {total_time:.3f} sec\n")


def process_query(question):
    log_info(f"Question: {question}")

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    # Live schema
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema='public'
    """)
    tables = cursor.fetchall()

    live_schema = ""
    for table in tables:
        table_name = table[0]
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name=%s
        """, (table_name,))
        columns = [row[0] for row in cursor.fetchall()]
        live_schema += f"\nTABLE: {table_name}\nCOLUMNS: {', '.join(columns)}\n"

    print("\n===== LIVE SCHEMA =====\n", live_schema)

    overall_start = time.time()
    retrieved_context, used_sources = retrieve_context(question)

    print("\n===== RETRIEVED CONTEXT =====\n", retrieved_context)

    is_pdf_query = (
        "PDF CONTEXT" in retrieved_context
        and "EXCEL CONTEXT" not in retrieved_context
    )

    if is_pdf_query:
        prompt = f"""
        Answer the question using ONLY the PDF context.
        Context: {retrieved_context}
        Question: {question}
        Rules:
        1. Give a direct answer.
        2. Do not generate SQL.
        3. Keep the answer concise.
        """
        answer, provider = generate_sql(prompt)
        conn.close()
        return {
            "type": "pdf",
            "answer": answer,
            "explanation": answer,
            "sql": "",
            "results": [],
            "columns": [],
            "sources": used_sources,
            "source_details": retrieved_context,
            "agent_trace": [
                "🧠 Query Understanding",
                "🔍 PDF Retrieval",
                "📄 Answer Generation"
            ],
            "provider": provider,
            "execution_time": round(time.time() - overall_start, 3)
        }

    prompt = f"""
    You are an expert SQL developer.

    LIVE DATABASE SCHEMA:
    {live_schema}

    RETRIEVED CONTEXT:
    {retrieved_context}

    Rules:
    1. Return ONLY SQL.
    2. No markdown.
    3. No explanation.
    4. Only SELECT queries.
    5. Use table names EXACTLY as shown in LIVE DATABASE SCHEMA.
    6. Use column names EXACTLY as shown in LIVE DATABASE SCHEMA.
    7. Never invent tables or columns.

    Question: {question}
    """

    sql, provider = generate_sql(prompt)
    sql = sql.replace("```sql", "").replace("```", "").strip()

    explanation = explain_sql(sql)
    validate_sql(sql)

    log_info(f"Generated SQL: {sql}")
    print("\n===== EXECUTING SQL =====\n", sql)

    cursor.execute(sql)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    total_time = time.time() - overall_start
    log_query(question, sql, provider, explanation, total_time)
    conn.close()

    return {
        "sql": sql,
        "results": rows,
        "columns": columns,
        "sources": used_sources,
        "source_details": retrieved_context,
        "agent_trace": [
            "🧠 Query Understanding",
            "🔍 Context Retrieval",
            "⚡ SQL Generation",
            "🛡 SQL Validation",
            "🗄 Database Execution",
            "📊 Result Formatting"
        ],
        "provider": provider,
        "explanation": explanation,
        "execution_time": round(total_time, 3)
    }