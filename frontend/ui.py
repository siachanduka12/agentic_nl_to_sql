import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)        
from main import process_query 
from ingestion.excel_to_postgres import excel_to_postgres
from ingestion.excel_ingestion import (
    add_excel_to_chroma,
    clear_excel_collection
)
from ingestion.pdf_ingestion import (
    add_pdf_to_chroma,
    clear_pdf_collection
)
from database.clear_postgres import clear_all_tables

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Discover Insights",
    page_icon="📊",
    layout="wide"
)

# ==================================================
# SESSION STATE
# ==================================================

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "question" not in st.session_state:
    st.session_state.question = ""   

if "files_processed" not in st.session_state:
    st.session_state.files_processed = False

if "last_files" not in st.session_state:
    st.session_state.last_files = ()

if st.button("🗑 Clear History"):

    st.session_state.query_history = []

    st.rerun()     

# ==================================================
# LIGHT CSS ONLY
# ==================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

h1{
    font-size:22px !important;
}

h2,h3{
    font-size:16px !important;
}

.stTextArea textarea{
    font-size:14px;
}

.small-text{
    font-size:13px;
    color:#6b7280;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# MAIN LAYOUT
# ==================================================

st.title("📊 Discover Insights")

st.caption(
    "Analyze information across your uploaded documents and datasets."
)

st.divider()

left, center, right = st.columns(
    [1.2, 2.8, 1.2]
)

# ==================================================
# LEFT PANEL
# ==================================================

with left:

    with st.container(border=True):

        uploaded_files = st.file_uploader(
        "Add Files",
        type=["pdf", "csv", "xlsx", "xls"],
        accept_multiple_files=True
    )
    if uploaded_files is None:
        uploaded_files = []

    current_files = (
        tuple(f.name for f in uploaded_files)
        if uploaded_files
        else ()
    )

    if current_files != st.session_state.last_files:
        st.session_state.files_processed = False
        st.session_state.last_files = current_files

    if uploaded_files and not st.session_state.files_processed:

        os.makedirs("data", exist_ok=True)

        clear_all_tables()
        clear_excel_collection()
        clear_pdf_collection()

        for file in uploaded_files:

            save_path = os.path.join(
                "data",
                file.name
            )

            with open(save_path, "wb") as f:
                f.write(file.getbuffer())

            if file.name.endswith(
                (".xlsx", ".xls")
            ):

                excel_to_postgres(save_path)

                #add_excel_to_chroma(save_path )

            elif file.name.endswith(".pdf"):

                add_pdf_to_chroma(
                    save_path
                )

        st.session_state.files_processed = True

        st.success(
            "Files processed successfully!"
        )
        file_count = len(uploaded_files) if 'uploaded_files' in locals() and uploaded_files else 0

        st.subheader(
        f"📂 Sources ({file_count})"
        )

        if uploaded_files:

            for file in uploaded_files:

                if file.name.endswith(".pdf"):
                    icon = "📄"

                elif file.name.endswith(".csv"):
                    icon = "📋"

                else:
                    icon = "📊"

                st.caption(
                    f"{icon} {file.name}"
                )

        else:

            st.caption(
                "No files uploaded"
            )

    with st.container(border=True):

        st.subheader("🕒 Recent Queries")

        if st.session_state.query_history:

            for q in reversed(
                st.session_state.query_history[-3:]
            ):

                short_q = (
                    q[:35] + "..."
                    if len(q) > 35
                    else q
                )

                st.caption(short_q)

        else:

            st.caption(
                "No queries yet"
            )

# ==================================================
# CENTER PANEL
# ==================================================

with center:


    question = st.text_area(
    "Question",
    value=st.session_state.question,
    placeholder="What would you like to know?",
    height=90,
    label_visibility="collapsed"
    )

    analyze = st.button(
        "Analyze",
        use_container_width=True
    )

# ==================================================
# RIGHT PANEL
# ==================================================

with right:

    with st.container(border=True):

        st.subheader("💡 Suggestions")

        if st.button("💡 Summarize PDF"):

            st.session_state.question = (
            "Summarize the uploaded PDF"
            )

            st.rerun()

        if st.button("💰 Highest Salary"):

            st.session_state.question = (
                "Which department has the highest salary?"
            )

            st.rerun()

        if st.button("👥 Employee Status"):

            st.session_state.question = (
                "Show employee status"
            )

            st.rerun()

    with st.container(border=True):

        st.subheader("📈 Overview")

        st.caption(
            f"📂 Files: {len(uploaded_files) if uploaded_files else 0}"
        )

        st.caption(
            f"🕒 Queries: {len(st.session_state.query_history)}"
        )
# ==================================================
# RESULTS
# ==================================================

if analyze and question:
    print("\n====================")
    print("BUTTON CLICKED")
    print("QUESTION:", question)
    print("====================")

    st.write("BUTTON CLICKED")

    st.session_state.query_history.append(
        question
    )

    try:
        result = process_query(question)
        print("\n===== RESULT RECEIVED =====")
        print(result)


    except Exception as e:
        print("\n===== UI ERROR =====")
        print(e)

        st.error(
            f"Error: {str(e)}"
        )

        st.stop()

    st.divider()

    if result.get("type") == "pdf":

        st.success(
            f"📄 {result['answer']}"
        )

    else:

        st.success(
            f"💡 {result['explanation']}"
        )

    if result.get("type") != "pdf":

        st.subheader("📝 Generated SQL")

        st.code(
            result["sql"],
            language="sql"
        )

    st.caption(
        f"Response Time: {result['execution_time']} sec"
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Results",
            "Sources",
            "Agent Trace"
        ]
    )

  

    # =====================================
    # RESULTS
    # =====================================

    with tab1:

        if result.get("type") == "pdf":

            st.info(
                "Answer generated from PDF content."
            )

            st.write(
                result["answer"]
            )

        else:

            df = pd.DataFrame(
                result["results"],
                columns=result["columns"]
            )

            st.dataframe(
                df,
                use_container_width=True
            )


    # =====================================
    # SOURCES
    # =====================================

    # =====================================
# SOURCES
# =====================================

    with tab2:

        st.subheader("📂 Sources Used")

        if uploaded_files:

            for file in uploaded_files:
                st.write(f"📄 {file.name}")

        else:

            st.info("No source files uploaded.")

    # =====================================
    # AGENT
    # =====================================

    with tab3:

        for step in result["agent_trace"]:
            st.write(f"✓ {step}")