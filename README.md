# 📊 Agentic NL-to-SQL with RAG

Transform natural language into accurate SQL queries using Agentic AI, Retrieval-Augmented Generation (RAG), Vector Search, and Large Language Models.

This project enables users to interact with structured data using plain English while automatically retrieving relevant schema and document context, generating SQL, validating queries, executing them against a database, and presenting results through an intuitive Streamlit interface.

---

## 🌟 Overview

Traditional database querying requires knowledge of SQL and database schemas. This project bridges that gap by allowing users to ask questions in natural language and receive accurate results without writing a single SQL statement.

The system combines:

* Agentic AI workflows
* Retrieval-Augmented Generation (RAG)
* ChromaDB Vector Search
* PostgreSQL
* Large Language Models (Groq/Gemini)
* Interactive Streamlit UI

to create an intelligent database assistant.

---

## 🏗️ System Architecture

```text
User Query
    │
    ▼
Query Understanding Agent
    │
    ▼
Context Retrieval Agent
    │
    ├── Database Schema
    ├── Excel Knowledge Base
    └── PDF Knowledge Base
    │
    ▼
SQL Generation Agent
    │
    ▼
SQL Validation Agent
    │
    ▼
Database Execution Agent
    │
    ▼
Result Formatting Agent
    │
    ▼
User Interface
```

---

## 🚀 Key Features

### 🤖 Multi-Agent Workflow

Every query follows a structured reasoning pipeline:

* Query Understanding
* Context Retrieval
* SQL Generation
* SQL Validation
* Database Execution
* Result Formatting

This improves transparency and reliability compared to direct prompt-to-SQL systems.

---

### 🔍 Retrieval-Augmented Generation (RAG)

The system retrieves relevant information before SQL generation from:

* Database schemas
* Uploaded Excel files
* Uploaded CSV files
* Uploaded PDF documents

This provides the LLM with contextual knowledge, improving query accuracy.

---

### 📂 Dynamic Data Ingestion

Upload files directly through the UI.

Supported formats:

* Excel (.xlsx, .xls)
* CSV
* PDF

Features:

* Automatic table creation
* Metadata extraction
* ChromaDB indexing
* Semantic retrieval

---

### 🧠 Intelligent SQL Generation

The system:

* Understands natural language questions
* Retrieves relevant schema context
* Generates SQL dynamically
* Validates queries before execution
* Reduces hallucinations using retrieved context

---

### 📈 Interactive Results

Users can view:

* Generated SQL
* Query results
* Retrieved context
* Agent workflow progress
* Processing status

---

## 🛠️ Technology Stack

| Component       | Technology       |
| --------------- | ---------------- |
| Frontend        | Streamlit        |
| Backend         | Python           |
| Database        | PostgreSQL       |
| Vector Database | ChromaDB         |
| Embeddings      | all-MiniLM-L6-v2 |
| LLM             | Groq             |
| Alternative LLM | Gemini           |
| ORM             | SQLAlchemy       |
| Data Processing | Pandas           |

---

## 📁 Project Structure

```text
agentic_nl_to_sql/
│
├── frontend/
│   └── ui.py
│
├── ingestion/
│   ├── excel_ingestion.py
│   ├── excel_to_postgres.py
│   └── pdf_ingestion.py
│
├── database/
│   └── chroma_setup.py
│
├── db/
│
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/siachanduka12/agentic_nl_to_sql.git

cd agentic_nl_to_sql
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key

DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
```

---

## ▶️ Running the Application

```bash
streamlit run frontend/ui.py
```

Application will be available at:

```text
http://localhost:8501
```

---

## 💬 Sample Queries

### Employee Dataset

```text
Show all employees.
```

```text
List employees earning more than 50000.
```

```text
Which department has the highest average salary?
```

### Student Dataset

```text
How many students belong to each department?
```

```text
Show students with CGPA above 8.
```

### Sales Dataset

```text
Which product generated the highest revenue?
```

```text
Show monthly sales trends.
```

---

## 📊 Example Workflow

### User Query

```text
Show all employees with salary greater than 50000
```

### Retrieved Context

```text
employees
├── id
├── name
├── department
├── salary
└── joining_year
```

### Generated SQL

```sql
SELECT *
FROM employees
WHERE salary > 50000;
```

### Result

```text
Records successfully retrieved and displayed.
```

---

## 🎯 Challenges Solved

* Schema-aware SQL generation
* Context-aware query understanding
* Excel and PDF knowledge retrieval
* Hallucination reduction using RAG
* Dynamic database ingestion
* Explainable AI workflow

---

## 🔮 Future Enhancements

* Multi-database support
* Conversational memory
* SQL optimization suggestions
* Query explanation engine
* Interactive schema graph visualization
* Agent performance monitoring
* Role-based access control

---

## 📸 Screenshots

Add screenshots of:

* Main Dashboard
* Agent Workflow Panel
* Generated SQL Output
* Query Results
* File Upload Interface

These significantly improve project presentation and recruiter visibility.

---

## 👩‍💻 Author

### Sia Chanduka

B.Tech Computer Science & Engineering

Built as part of an Agentic AI and RAG-based Natural Language Querying project focused on intelligent database interaction using Large Language Models.
