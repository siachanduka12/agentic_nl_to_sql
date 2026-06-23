import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import process_query
from ingestion.excel_to_postgres import excel_to_postgres
from ingestion.excel_ingestion import add_excel_to_chroma, clear_excel_collection
from ingestion.pdf_ingestion import add_pdf_to_chroma, clear_pdf_collection
from database.clear_postgres import clear_all_tables

st.set_page_config(page_title="Discover Insights", page_icon="📊", layout="wide")

# Session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "question" not in st.session_state:
    st.session_state.question = ""
if "last_file_names" not in st.session_state:
    st.session_state.last_file_names = []

if st.button("🗑 Clear History"):
    st.session_state.query_history = []
    st.rerun()

st.markdown("""
<style>
.block-container { padding-top:1rem; }
h1 { font-size:22px !important; }
h2,h3 { font-size:16px !important; }
.stTextArea textarea { font-size:14px; }
.small-text { font-size:13px; color:#6b7280; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
padding:25px;
border-radius:18px;
background:linear-gradient(90deg,#0f172a,#1e293b);
color:white;
color:white;
margin-bottom:15px;
">

<h1 style="margin:0;">
🤖 AGENTIC NLP TO SQL 
</h1>

<p style="margin-top:10px;font-size:18px;">
Talk to your Excel files, PDFs and databases using natural language.
</p>

</div>
""", unsafe_allow_html=True)
st.divider()

center, right = st.columns([3.5, 1])

with center:

    with st.container(border=True):

        uploaded_files = st.file_uploader(
            "📂 Upload Files",
            type=["pdf", "csv", "xlsx", "xls"],
            accept_multiple_files=True
        )

    with st.container(border=True):

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric(
                "📂 Files",
                len(uploaded_files) if uploaded_files else 0
            )

        with k2:
            st.metric(
                "💬 Queries",
                len(st.session_state.query_history)
            )

        with k3:
            st.metric(
                "🤖 Agent",
                "Active"
            )

        with k4:
            st.metric(
                "🗄 Status",
                "Ready"
            )

    if not st.session_state.query_history:

        st.info("""
        👋 Welcome to Data Insights Assistant

        Upload Excel or PDF files and ask questions like:

        • Show all students
        • Highest salary department
        • Summarize uploaded PDF
        • Show sales by city
        """)

    question = st.text_area(
        "Question",
        value=st.session_state.question,
        placeholder="What would you like to know?",
        height=90,
        label_visibility="collapsed"
    )

    analyze = st.button(
        "🚀 Analyze",
        use_container_width=True
    )

with right:
    with st.container(border=True):
        st.subheader("💡 Suggestions")
        if st.button("💡 Summarize PDF"):
            st.session_state.question = "Summarize the uploaded PDF"
            st.rerun()
        if st.button("💰 Highest Salary"):
            st.session_state.question = "Which department has the highest salary?"
            st.rerun()
        if st.button("👥 Employee Status"):
            st.session_state.question = "Show employee status"
            st.rerun()

    with st.container(border=True):
        st.subheader("📈 Overview")
        st.caption(f"📂 Files: {len(uploaded_files) if uploaded_files else 0}")
        st.caption(f"🕒 Queries: {len(st.session_state.query_history)}")

    with st.container(border=True):

        st.subheader("🕒 Recent Queries")

        if st.session_state.query_history:

            for q in reversed(
                st.session_state.query_history[-5:]
            ):
                st.caption(f"• {q}")

        else:
            st.caption("No queries yet")    

# ── File ingestion (only when file list changes) ──────────────────────────────
if uploaded_files:
    current_file_names = sorted([f.name for f in uploaded_files])
 
    if current_file_names != st.session_state.last_file_names:
        with st.spinner("Processing uploaded files..."):
            clear_all_tables()
            clear_excel_collection()
            clear_pdf_collection()
 
            for file in uploaded_files:
                if file.name.endswith((".xlsx", ".xls", ".csv")):
                    file.seek(0)
                    excel_to_postgres(file)
                    file.seek(0)
                    add_excel_to_chroma(file)
                    print(f"Excel processed: {file.name}")
                elif file.name.endswith(".pdf"):
                    file.seek(0)
                    add_pdf_to_chroma(file)
                    print(f"PDF processed: {file.name}")
 
        st.session_state.last_file_names = current_file_names
        st.success("Files processed successfully!")
 
    # ── File list with clickable Excel/CSV preview ─────────────────────────────
    with st.container(border=True):
        st.markdown("#### 📂 Uploaded Files")
 
        for file in uploaded_files:
            ext = file.name.rsplit(".", 1)[-1].lower()
 
            if ext in ("xlsx", "xls", "csv"):
                # Expandable preview panel for tabular files
                with st.expander(f"📊 {file.name}  —  click to preview"):
                    try:
                        file.seek(0)
                        if ext == "csv":
                            df_preview = pd.read_csv(file)
                        else:
                            df_preview = pd.read_excel(file)
 
                        rows, cols = df_preview.shape
                        c1, c2 = st.columns(2)
                        c1.metric("Rows", rows)
                        c2.metric("Columns", cols)
 
                        st.dataframe(
                            df_preview.head(50),
                            use_container_width=True,
                            height=300,
                        )
 
                        if rows > 50:
                            st.caption(
                                f"Showing first 50 of {rows} rows."
                            )
 
                    except Exception as e:
                        st.error(f"Could not preview file: {e}")
 
            else:
                # Non-tabular file (PDF) — just show name with icon
                st.markdown(f"📄 **{file.name}**")


# ── Query execution ───────────────────────────────────────────────────────────
if analyze and question:
    if not uploaded_files:
        st.warning("Please upload at least one file before querying.")
        st.stop()

    st.session_state.query_history.append(question)

    try:
        result = process_query(question)
    except Exception as e:
        print("\n===== UI ERROR =====\n", e)
        st.error(f"Error: {str(e)}")
        st.stop()

    #st.divider()

    if result.get("type") == "pdf":
        st.success(f"📄 {result['answer']}")
    else:
        st.success(f"💡 {result['explanation']}")

    if result.get("type") != "pdf":
        st.subheader("📝 Generated SQL")
        st.code(result["sql"], language="sql")

        st.download_button(
            "📥 Download SQL",
            result["sql"],
            file_name="query.sql"
        )

    st.caption(f"Response Time: {result['execution_time']} sec")

    tab1, tab2, tab3 = st.tabs(
        [
            "📊 Results",
            "📂 Sources",
            "🤖 Agent Trace"
        ]
    )

    with tab1:
        if result.get("type") == "pdf":
            st.info("Answer generated from PDF content.")
            st.write(result["answer"])
        else:
            df = pd.DataFrame(
                result["results"],
                columns=result["columns"]
            )

            m1, m2, m3 = st.columns(3)

            m1.metric(
                "Rows",
                len(df)
            )

            m2.metric(
                "Columns",
                len(df.columns)
            )

            m3.metric(
                "Response",
                f"{result['execution_time']} sec"
            )

            st.dataframe(
                df,
                use_container_width=True
            )
            csv = df.to_csv(index=False)

            st.download_button(
                "⬇ Download CSV",
                csv,
                file_name="results.csv",
                mime="text/csv"
            )

            if len(df.columns) >= 2:

                try:

                    numeric_cols = df.select_dtypes(
                        include="number"
                    ).columns

                    if len(numeric_cols) > 0:

                        st.subheader("📈 Visualization")

                        chart_col = numeric_cols[0]

                        st.bar_chart(
                            df.set_index(
                                df.columns[0]
                            )[chart_col]
                        )

                except:
                    pass

        
    with tab2:
        st.subheader("📂 Sources Used")

        if result.get("sources"):
            for src in result["sources"]:
                st.write(f"📄 {src}")
        else:
            st.info("No sources identified.")

        # Show source details — table names and columns
        if result.get("source_details"):
            st.divider()
            st.subheader("📋 Context Details")

            details = result["source_details"]

            # Parse and display each context block cleanly
            for block in details.split("\nEXCEL CONTEXT"):
                if "TABLE NAME:" in block:
                    lines = block.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line.startswith("TABLE NAME:"):
                            st.markdown(f"**🗄 Table:** `{line.replace('TABLE NAME:', '').strip()}`")
                        elif line.startswith("FILE:"):
                            st.markdown(f"**📄 File:** {line.replace('FILE:', '').strip()}")
                        elif line.startswith("COLUMNS:"):
                            st.markdown(f"**📊 Columns:** `{line.replace('COLUMNS:', '').strip()}`")
                    st.divider()

    with tab3:

        st.subheader("🤖 Agent Workflow")

        for i, step in enumerate(
            result["agent_trace"],
            start=1
        ):

            st.markdown(
                f"✅ **Step {i}:** {step}"
            )