import sqlite3

# ==================================
# DATABASE CONNECTION
# ==================================

conn = sqlite3.connect("./db/company.db")
cursor = conn.cursor()

# ==================================
# CREATE TABLES
# ==================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary REAL,
    joining_year INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    product TEXT,
    amount REAL,
    year INTEGER
)
""")

# ==================================
# CLEAR OLD DATA (OPTIONAL)
# ==================================

cursor.execute("DELETE FROM employees")
cursor.execute("DELETE FROM sales")

# ==================================
# INSERT EMPLOYEE DATA
# ==================================

employees_data = [
    (1, "Alice", "IT", 70000, 2019),
    (2, "Bob", "HR", 50000, 2021),
    (3, "Charlie", "IT", 80000, 2020),
    (4, "Diana", "Finance", 60000, 2018),
    (5, "Eve", "IT", 75000, 2022)
]

cursor.executemany("""
INSERT INTO employees
VALUES (?, ?, ?, ?, ?)
""", employees_data)

# ==================================
# INSERT SALES DATA
# ==================================

sales_data = [
    (1, "Laptop", 50000, 2021),
    (2, "Phone", 30000, 2022),
    (3, "Tablet", 20000, 2021),
    (4, "Monitor", 15000, 2023)
]

cursor.executemany("""
INSERT INTO sales
VALUES (?, ?, ?, ?)
""", sales_data)

# ==================================
# SAVE & CLOSE
# ==================================

conn.commit()
conn.close()

print("Database setup completed successfully!")