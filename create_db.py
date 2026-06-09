import sqlite3

conn = sqlite3.connect("company.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary REAL,
    joining_year INTEGER
)
""")

cursor.executemany("""
INSERT INTO employees
(id, name, department, salary, joining_year)
VALUES (?, ?, ?, ?, ?)
""", [
    (1, "Alice", "IT", 70000, 2019),
    (2, "Bob", "HR", 50000, 2021),
    (3, "Charlie", "IT", 80000, 2020),
    (4, "Diana", "Finance", 60000, 2018),
    (5, "Eve", "IT", 75000, 2022)
])

conn.commit()
conn.close()

print("Database created successfully!")