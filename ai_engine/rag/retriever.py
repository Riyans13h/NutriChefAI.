from typing import List
from chromadb import Client
from chromadb.config import Settings


class RAGRetriever:
    """
    Handles semantic retrieval of recipe documents
    from ChromaDB for the RAG pipeline.
    """

    def __init__(
        self,
        persist_directory: str = "ai_engine/vector_store/chroma_db",
        collection_name: str = "recipes"
    ):
        self.client = Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def retrieve(self, query_embedding: List[float], top_k: int = 5) -> List[str]:
        """
        Retrieve top-k relevant recipe documents
        based on cosine similarity.

        Args:
            query_embedding (List[float]): Embedded user query
            top_k (int): Number of documents to retrieve

        Returns:
            List[str]: Retrieved recipe texts
        """

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        documents = results.get("documents", [])

        # Flatten list of lists
        return [doc for sublist in documents for doc in sublist]
