from app.embedding import create_embeddings
from app.vector_store import collection


def search_documents(
    query: str,
    document_id: str,
    n_results: int = 5,
) -> list[dict]:

    query_embedding = create_embeddings(
        [query]
    )[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "document_id": document_id
        },
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        retrieved_chunks.append(
            {
                "text": document,
                "filename": metadata["filename"],
                "page_number": metadata["page_number"],
                "chunk_id": metadata["chunk_id"],
                "distance": distance,
            }
        )

    return retrieved_chunks