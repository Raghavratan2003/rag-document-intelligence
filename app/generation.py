from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


def generate_answer(
    question: str,
    retrieved_chunks: list[dict],
) -> dict:

    context_parts = []

    for index, chunk in enumerate(retrieved_chunks):
        context_parts.append(
            f"""
SOURCE {index + 1}
File: {chunk["filename"]}
Page: {chunk["page_number"]}

{chunk["text"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a document analysis assistant.

Answer the user's question using ONLY the information
contained in the provided sources.

Rules:
1. Do not invent facts or numbers.
2. If the answer cannot be found in the sources, say:
   "The information was not found in the document."
3. Identify which source numbers directly support your answer.
4. Return your response as valid JSON.

Required JSON format:

{{
    "answer": "Your answer here",
    "source_numbers": [1, 2]
}}

Sources:

{context}

User question:

{question}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    return response.output_text