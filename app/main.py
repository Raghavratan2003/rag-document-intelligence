import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.analytics import calculate_document_stats
from app.chunking import create_chunks
from app.embedding import create_embeddings
from app.generation import generate_answer
from app.ingestion import extract_text_from_pdf
from app.retrieval import search_documents
from app.vector_store import (
    add_chunks,
    collection,
    document_exists,
)
from app.document_manager import calculate_document_id


app = FastAPI(
    title="Production RAG Document Intelligence System"
)


app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static",
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


class SearchRequest(BaseModel):
    query: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Check file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Check filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    file_path = UPLOAD_DIR / file.filename

    # Save file
    contents = await file.read()

    document_id = calculate_document_id(contents)

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if document_exists(document_id):
        return {
            "filename": file.filename,
            "status": "Document already indexed.",
        }

    file_path.write_bytes(contents)

    # Extract text
    try:
        pages = extract_text_from_pdf(
            str(file_path)
        )
    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Could not read the PDF. The file may be corrupted.",
        )

    # Check extracted text
    if not pages:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="No readable text was found in the PDF.",
        )

    # Create chunks
    chunks = create_chunks(pages)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Could not create searchable text chunks.",
        )

    # Document statistics
    stats = calculate_document_stats(
        pages,
        chunks,
    )

    # Create embeddings
    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = create_embeddings(texts)

    # Store in vector database
    add_chunks(
    chunks=chunks,
    embeddings=embeddings,
    filename=file.filename,
    document_id=document_id,
    )

    return {
        "filename": file.filename,
        "statistics": stats,
        "status": "Document indexed successfully",
    }


@app.post("/search")
def search(request: SearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a search query.",
        )

    if collection.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents have been indexed yet.",
        )

    results = search_documents(
        request.query
    )

    return {
        "query": request.query,
        "results": results,
    }


@app.post("/ask")
def ask(request: SearchRequest):

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    if collection.count() == 0:
        raise HTTPException(
            status_code=400,
            detail="Please upload a document first.",
        )

    results = search_documents(
        request.query
    )

    raw_response = generate_answer(
        question=request.query,
        retrieved_chunks=results,
    )

    try:
        response = json.loads(raw_response)

    except json.JSONDecodeError:
        return {
            "question": request.query,
            "answer": raw_response,
            "sources": [],
        }

    source_numbers = response.get(
        "source_numbers",
        [],
    )

    sources = []

    for number in source_numbers:

        index = number - 1

        if 0 <= index < len(results):

            result = results[index]

            source = {
                "filename": result["filename"],
                "page_number": result["page_number"],
            }

            if source not in sources:
                sources.append(source)

    return {
        "question": request.query,
        "answer": response.get(
            "answer",
            "",
        ),
        "sources": sources,
    }