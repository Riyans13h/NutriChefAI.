"""
Embedding Service
-----------------
Responsible for:
- Converting recipes into embedding documents
- Generating embeddings using OpenAI
- Persisting embeddings in ChromaDB
"""

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.database import MySQLDatabase
from flask import current_app


class EmbeddingService:
    """
    Handles embedding generation and storage.
    """

    @staticmethod
    def build_recipe_documents():
        """
        Converts SQL recipe data into text documents.

        Returns:
            list[str], list[int]
        """

        recipes = MySQLDatabase.execute_query(
            query="""
                SELECT r.recipe_id, r.name, r.base_steps,
                       GROUP_CONCAT(i.name SEPARATOR ', ') AS ingredients
                FROM recipes r
                JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
                JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                GROUP BY r.recipe_id
            """,
            fetchall=True
        )

        documents = []
        metadatas = []

        for recipe in recipes:
            text = (
                f"Recipe Name: {recipe['name']}\n"
                f"Ingredients: {recipe['ingredients']}\n"
                f"Steps: {recipe['base_steps']}"
            )

            documents.append(text)
            metadatas.append({"recipe_id": recipe["recipe_id"]})

        return documents, metadatas

    @staticmethod
    def generate_and_store_embeddings():
        """
        Generates embeddings and stores them in ChromaDB.
        """

        documents, metadatas = EmbeddingService.build_recipe_documents()

        if not documents:
            return

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=current_app.config["OPENAI_API_KEY"]
        )

        Chroma.from_texts(
            texts=documents,
            metadatas=metadatas,
            embedding=embeddings,
            persist_directory=current_app.config["CHROMA_DB_DIR"]
        )
