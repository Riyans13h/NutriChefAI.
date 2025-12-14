"""
Builds and stores embeddings for recipes into ChromaDB
using OpenAI embedding models.

Run this file ONLY when recipes are added or updated.
"""

import os
from typing import List
from openai import OpenAI
from chromadb import Client
from chromadb.config import Settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

EMBEDDING_MODEL = "text-embedding-3-small"


# -------------------- Embedding Function --------------------
def embed_text(text: str) -> List[float]:
    """
    Generates OpenAI embeddings for given text.
    """

    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


# -------------------- Build Embeddings --------------------
def build_recipe_embeddings(recipes: List[str]) -> None:
    client = Client(
        Settings(
            persist_directory="ai_engine/vector_store/chroma_db",
            anonymized_telemetry=False
        )
    )

    collection = client.get_or_create_collection(name="recipes")

    for idx, recipe in enumerate(recipes):
        embedding = embed_text(recipe)

        collection.add(
            ids=[str(idx)],
            documents=[recipe],
            embeddings=[embedding]
        )

    print(f"Successfully stored {len(recipes)} recipe embeddings")


# -------------------- Entry Point --------------------
if __name__ == "__main__":
    # Example: this data should come from DB in real systems
    recipe_corpus = [
        "Grilled chicken salad with olive oil and vegetables",
        "Vegetable stir fry with tofu and soy sauce",
        "Oats porridge with fruits and nuts"
    ]

    build_recipe_embeddings(recipe_corpus)
