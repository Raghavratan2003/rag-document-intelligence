def calculate_document_stats(
    pages: list[dict],
    chunks: list[dict],
) -> dict:

    if pages:
        total_words = sum(
            len(page["text"].split())
            for page in pages
        )

        pages_with_text = len(pages)

    else:
        total_words = sum(
            len(chunk["text"].split())
            for chunk in chunks
        )

        pages_with_text = len(
            set(
                chunk["page_number"]
                for chunk in chunks
            )
        )

    total_chunk_words = sum(
        len(chunk["text"].split())
        for chunk in chunks
    )

    average_words_per_page = (
        total_words / pages_with_text
        if pages_with_text
        else 0
    )

    average_words_per_chunk = (
        total_chunk_words / len(chunks)
        if chunks
        else 0
    )

    return {
        "pages_with_text": pages_with_text,
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