import sqlite3
from groq import Groq

# ==================================
# GROQ SETUP
# ==================================

client = Groq(
    api_key="api"
)

# ==================================
# SQL VALIDATION AGENT
# ==================================

def validate_sql(sql):
    forbidden = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE"
    ]

    sql_upper = sql.upper()

    for word in forbidden:
        if word in sql_upper:
            raise Exception(f"Forbidden SQL detected: {word}")

    return True

# ==================================
# DATABASE SETUP
# ==================================

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

# Employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary REAL,
    joining_year INTEGER
)
""")

# Sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    product TEXT,
    amount REAL,
    year INTEGER
)
""")

# Insert sample employees only once
cursor.execute("SELECT COUNT(*) FROM employees")

if cursor.fetchone()[0] == 0:
    cursor.executemany("""
    INSERT INTO employees
    VALUES (?, ?, ?, ?, ?)
    """, [
        (1, "Alice", "IT", 70000, 2019),
        (2, "Bob", "HR", 50000, 2021),
        (3, "Charlie", "IT", 80000, 2020),
        (4, "Diana", "Finance", 60000, 2018),
        (5, "Eve", "IT", 75000, 2022)
    ])

# Insert sample sales only once
cursor.execute("SELECT COUNT(*) FROM sales")

if cursor.fetchone()[0] == 0:
    cursor.executemany("""
    INSERT INTO sales
    VALUES (?, ?, ?, ?)
    """, [
        (1, "Laptop", 50000, 2021),
        (2, "Phone", 30000, 2022),
        (3, "Tablet", 20000, 2021),
        (4, "Monitor", 15000, 2023)
    ])

conn.commit()

# ==================================
# USER QUESTION
# ==================================

question = input("\nAsk a question: ")

prompt = f"""
You are an expert SQL developer.

Database Schema:

employees(
    id,
    name,
    department,
    salary,
    joining_year
)

sales(
    id,
    product,
    amount,
    year
)

Rules:
1. Return ONLY SQL.
2. No markdown.
3. No explanation.
4. Only SELECT queries.
5. Use the correct table and columns.

Question:
{question}
"""

# ==================================
# SQL GENERATION AGENT
# ==================================

def generate_sql(prompt):
    try:
        print("Using DeepSeek...")

        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("DeepSeek failed:", e)

        print("Switching to Llama...")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

sql = generate_sql(prompt)
sql = sql.strip()

# Remove markdown if model accidentally returns it
sql = sql.replace("```sql", "")
sql = sql.replace("```", "")
sql = sql.strip()

print("\nGenerated SQL:")
print(sql)

# ==================================
# VALIDATION AGENT
# ==================================

try:
    validate_sql(sql)

    # ==================================
    # EXECUTION AGENT
    # ==================================

    cursor.execute(sql)

    rows = cursor.fetchall()

    print("\nResults:")

    if len(rows) == 0:
        print("No records found.")
    else:
        for row in rows:
            print(row)

except Exception as e:
    print("\nError:")
    print(e)

finally:
    conn.close()
