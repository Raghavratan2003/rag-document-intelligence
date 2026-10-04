import streamlit as st
from pathlib import Path

from app.analytics import calculate_document_stats
from app.chunking import create_chunks
from app.document_manager import calculate_document_id
from app.embedding import create_embeddings
from app.generation import generate_answer
from app.ingestion import extract_text_from_pdf
from app.retrieval import search_documents
from app.vector_store import (
    document_exists,
    get_document_chunks,
    get_document_id,
    add_chunks,
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
)


st.title("📄 Production RAG Document Intelligence")
st.caption(
    "Upload a PDF, ask questions, and get answers with page-level citations."
)


# ---------------------------------------------------------
# Upload Document
# ---------------------------------------------------------

st.header("1. Upload Document")

uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"],
)

if uploaded_file is not None:

    if st.button("Process Document", type="primary"):

        file_bytes = uploaded_file.getvalue()

        if not file_bytes:
            st.error("The uploaded file is empty.")
            st.stop()

        document_id = calculate_document_id(file_bytes)

        # Check for duplicate document
        if document_exists(document_id):

            existing_chunks = get_document_chunks(document_id)

            stats = calculate_document_stats(
                [],
                existing_chunks,
            )

            st.session_state["filename"] = uploaded_file.name
            st.session_state["document_id"] = document_id

            st.success("Document is already indexed.")

        else:

            file_path = UPLOAD_DIR / uploaded_file.name

            file_path.write_bytes(file_bytes)

            with st.spinner("Extracting text..."):
                pages = extract_text_from_pdf(str(file_path))

            if not pages:
                st.error(
                    "No readable text was found in this PDF."
                )
                st.stop()

            with st.spinner("Creating document chunks..."):
                chunks = create_chunks(pages)

            stats = calculate_document_stats(
                pages,
                chunks,
            )

            with st.spinner("Creating embeddings..."):
                embeddings = create_embeddings(
                    [chunk["text"] for chunk in chunks]
                )

            with st.spinner("Indexing document..."):
                add_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    filename=uploaded_file.name,
                    document_id=document_id,
                )

            st.session_state["filename"] = uploaded_file.name
            st.session_state["document_id"] = document_id

            st.success("Document indexed successfully.")


# ---------------------------------------------------------
# Document Analytics
# ---------------------------------------------------------

if "filename" in st.session_state:

    st.header("2. Document Analytics")

    filename = st.session_state["filename"]
    document_id = st.session_state["document_id"]

    chunks = get_document_chunks(document_id)

    stats = calculate_document_stats(
        [],
        chunks,
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pages",
        stats["pages_with_text"],
    )

    col2.metric(
        "Chunks",
        stats["total_chunks"],
    )

    col3.metric(
        "Words",
        f'{stats["total_words"]:,}',
    )

    col4.metric(
        "Avg. Words / Page",
        stats["average_words_per_page"],
    )

    st.info(f"Current document: **{filename}**")


# ---------------------------------------------------------
# Question Answering
# ---------------------------------------------------------

if "filename" in st.session_state:

    st.header("3. Ask Questions")

    question = st.text_area(
        "Ask a question about the uploaded document",
        placeholder="Example: What was the company's revenue in 2025?",
        height=100,
    )

    if st.button("Ask Question"):

        if not question.strip():
            st.warning("Please enter a question.")
            st.stop()

        with st.spinner("Searching the document..."):

            retrieved_chunks = search_documents(
                query=question,
                document_id=st.session_state["document_id"],
                n_results=5,
            )

        if not retrieved_chunks:
            st.warning(
                "No relevant information was found."
            )
            st.stop()

        with st.spinner("Generating answer..."):

            result = generate_answer(
                question,
                retrieved_chunks,
            )

        try:
            import json

            result = json.loads(result)

            answer = result["answer"]
            source_numbers = result.get(
                "source_numbers",
                [],
            )

        except Exception:
            answer = result
            source_numbers = []

        st.subheader("Answer")

        st.write(answer)

        st.subheader("Sources")

        if source_numbers:

            for source_number in source_numbers:

                index = source_number - 1

                if 0 <= index < len(retrieved_chunks):

                    source = retrieved_chunks[index]

                    st.write(
                        f"📄 **{source['filename']}** "
                        f"— Page **{source['page_number']}**"
                    )

        else:

            st.write(
                "No specific sources were identified."
            )