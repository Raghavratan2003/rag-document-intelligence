import chromadb


chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="documents"
)


def document_exists(document_id: str) -> bool:

    results = collection.get(
        where={
            "document_id": document_id
        },
        limit=1,
    )

    return len(results["ids"]) > 0


def add_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    filename: str,
    document_id: str,
):
    ids = []
    documents = []
    metadatas = []

    for chunk, embedding in zip(
        chunks,
        embeddings,
    ):

        chunk_id = (
            f"{document_id}_{chunk['chunk_id']}"
        )

        ids.append(chunk_id)

        documents.append(
            chunk["text"]
        )

        metadatas.append(
            {
                "filename": filename,
                "page_number": chunk["page_number"],
                "chunk_id": chunk["chunk_id"],
                "document_id": document_id,
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )