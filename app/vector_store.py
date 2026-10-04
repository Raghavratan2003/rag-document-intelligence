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


def get_document_id(filename: str) -> str | None:

    results = collection.get(
        where={
            "filename": filename
        },
        limit=1,
    )

    if not results["metadatas"]:
        return None

    return results["metadatas"][0]["document_id"]


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

def get_document_chunks(document_id: str) -> list[dict]:
    results = collection.get(
        where={
            "document_id": document_id
        }
    )

    chunks = []

    for document, metadata in zip(
        results["documents"],
        results["metadatas"],
    ):
        chunks.append(
            {
                "text": document,
                "page_number": metadata["page_number"],
                "chunk_id": metadata["chunk_id"],
            }
        )

    return chunks