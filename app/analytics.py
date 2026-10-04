def calculate_document_stats(
    pages: list[dict],
    chunks: list[dict],
) -> dict:

    total_words = sum(
        len(page["text"].split())
        for page in pages
    )

    total_chunk_words = sum(
        len(chunk["text"].split())
        for chunk in chunks
    )

    average_words_per_page = (
        total_words / len(pages)
        if pages
        else 0
    )

    average_words_per_chunk = (
        total_chunk_words / len(chunks)
        if chunks
        else 0
    )

    return {
        "pages_with_text": len(pages),
        "total_chunks": len(chunks),
        "total_words": total_words,
        "average_words_per_page": round(
            average_words_per_page,
            2,
        ),
        "average_words_per_chunk": round(
            average_words_per_chunk,
            2,
        ),
    }