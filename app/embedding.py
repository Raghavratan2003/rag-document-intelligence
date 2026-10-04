from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()


def create_embeddings(
    texts: list[str],
    batch_size: int = 100,
) -> list[list[float]]:

    all_embeddings = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )

        embeddings = [item.embedding for item in response.data]

        all_embeddings.extend(embeddings)

    return all_embeddings