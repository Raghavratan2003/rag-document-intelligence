# Production RAG Document Intelligence System

A document question-answering system built using **Retrieval-Augmented Generation (RAG)** that allows users to upload PDF documents, search their contents using natural language, and receive AI-generated answers with page-level source citations.

---

## Features

- Upload and process PDF documents
- Extract text while preserving page numbers
- Split documents into overlapping chunks
- Generate semantic embeddings using OpenAI
- Store and search embeddings using ChromaDB
- Perform semantic document retrieval
- Generate answers using GPT-5-mini
- Provide page-level source citations
- Prevent duplicate document indexing using SHA-256 hashing
- Restrict retrieval to the selected document
- Display document analytics
- Interactive Streamlit interface

---

## Architecture

```text
                         PDF Document
                              │
                              ▼
                           PyMuPDF
                              │
                              ▼
                       Text Extraction
                              │
                              ▼
                      Document Chunking
                              │
                              ▼
                     OpenAI Embeddings
                              │
                              ▼
                           ChromaDB
                              │
                              │
                              ▼
                         User Query
                              │
                              ▼
                       Query Embedding
                              │
                              ▼
                     Semantic Retrieval
                              │
                              ▼
                       Relevant Chunks
                              │
                              ▼
                          GPT-5-mini
                              │
                              ▼
                      Answer + Citations
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | User interface |
| PyMuPDF | PDF text extraction |
| OpenAI API | Embeddings and answer generation |
| ChromaDB | Vector database |
| uv | Python dependency management |

---

## Project Structure

```text
production-rag-document-intelligence/
│
├── app/
│   ├── analytics.py
│   ├── chunking.py
│   ├── document_manager.py
│   ├── embeddings.py
│   ├── generation.py
│   ├── ingestion.py
│   ├── retrieval.py
│   └── vector_store.py
│
├── data/
│   └── uploads/
│       └── .gitkeep
│
├── streamlit_app.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## How It Works

### 1. Document Ingestion

The user uploads a PDF through the Streamlit interface.

PyMuPDF extracts text from each page while preserving the original page number.

### 2. Text Chunking

The extracted text is divided into overlapping chunks to improve retrieval quality.

Current configuration:

- **Chunk size:** 1000 characters
- **Chunk overlap:** 200 characters

Each chunk retains its source page number.

### 3. Embedding Generation

Each document chunk is converted into a semantic vector representation using OpenAI's `text-embedding-3-small` model.

### 4. Vector Storage

Document chunks and their embeddings are stored in ChromaDB.

Each chunk contains metadata including:

- Filename
- Page number
- Chunk ID
- Document ID

### 5. Semantic Retrieval

When the user asks a question, the question is converted into an embedding.

The system performs a similarity search against the stored document embeddings and retrieves the most relevant chunks.

Retrieval is restricted to the currently selected document.

### 6. Answer Generation

The retrieved chunks are passed to GPT-5-mini.

The model is instructed to:

- Answer using only the retrieved document information
- Avoid inventing facts or numbers
- Return a fallback when the information is not available
- Identify the sources supporting the answer

### 7. Source Citations

The application maps the retrieved source references back to the original PDF and displays the corresponding page numbers.

Example:

```text
Question:
What was the company's revenue in 2025?

Answer:
The company's revenue was $X billion in 2025.

Source:
Annual_Report.pdf — Page 42
```

---

## Document Analytics

After processing a document, the application displays:

- Number of pages
- Number of chunks
- Total words
- Average words per page

---

## Duplicate Document Detection

Each uploaded PDF is assigned a **SHA-256 document ID** based on its file contents.

If the same document is uploaded again, the system detects that it has already been indexed and avoids generating duplicate embeddings.

---

## Document-Specific Retrieval

Every document chunk is associated with a unique document ID.

When a user asks a question, retrieval is restricted to the currently selected document.

This prevents information from different uploaded documents from being mixed together.

---

## Example Questions

The system can answer questions such as:

```text
What was the company's revenue in 2025?

What were the company's major business segments?

How many employees did the company have?

What were the main risks mentioned in the report?

What was the year-over-year revenue growth?

What were the company's main sources of revenue?
```

---

## Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/Raghavratan2003/rag-document-intelligence]
cd production-rag-document-intelligence
```

### 2. Install Dependencies

This project uses `uv` for Python dependency management.

```bash
uv sync
```

### 3. Configure the OpenAI API Key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

Do not commit the `.env` file to GitHub.

### 4. Run the Application

```bash
uv run streamlit run streamlit_app.py
```

The application will open in your browser.

---

## Limitations

- Currently optimized for text-based PDFs.
- Scanned PDFs requiring OCR are not supported.
- ChromaDB is stored locally.
- Uploaded documents are stored locally.
- The project is designed as a portfolio and recruiter demonstration rather than a fully managed production deployment.

---

## Future Improvements

- OCR support for scanned documents
- Hybrid keyword and semantic retrieval
- Retrieval reranking
- Cloud-based vector database
- Persistent document management
- Authentication and multi-user support
- Automated retrieval and answer-quality evaluation
- Support for additional document formats

---
