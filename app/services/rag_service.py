"""
RAG Service
-----------
Responsible for:
- Retrieving grounded recipe context from ChromaDB
- Combining SQL data with vector search results
- Applying reinforcement learning preference weights
- Preparing input for the LLM
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from flask import current_app

from app.database import MySQLDatabase
from app.services.rl_engine import RLEngine
from app.services.llm_service import LLMService


class RAGService:
    """
    Retrieval-Augmented Generation orchestration.
    """

    @staticmethod
    def retrieve_recipe_context(recipe_id: int):
        """
        Retrieves grounded recipe text from ChromaDB.
        """

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=current_app.config["OPENAI_API_KEY"]
        )

        vector_store = Chroma(
            persist_directory=current_app.config["CHROMA_DB_DIR"],
            embedding_function=embeddings
        )

        results = vector_store.get(
            where={"recipe_id": recipe_id}
        )

        if not results or not results.get("documents"):
            return ""

        return results["documents"][0]

    @staticmethod
    def generate_final_recipe(recipe_id: int, user_id: int):
        """
        Generates the final personalized recipe using RAG + LLM.
        """

        # 1. Retrieve grounded context
        recipe_context = RAGService.retrieve_recipe_context(recipe_id)

        # 2. Fetch nutrition data
        nutrition = MySQLDatabase.execute_query(
            query="""
                SELECT calories, protein, carbs, fat
                FROM nutrition
                WHERE recipe_id = %s
            """,
            params=(recipe_id,),
            fetchone=True
        )

        # 3. Fetch recipe name
        recipe = MySQLDatabase.execute_query(
            query="SELECT name FROM recipes WHERE recipe_id = %s",
            params=(recipe_id,),
            fetchone=True
        )

        # 4. RL preference weight
        preference_weight = RLEngine.get_preference_weight(
            user_id=user_id,
            recipe_id=recipe_id
        )

        # 5. Build prompt
        prompt = f"""
You are a professional chef assistant.

Rules:
- Use ONLY the information provided below.
- Do NOT add new ingredients.
- Do NOT invent nutrition values.
- Rewrite steps clearly and concisely.

Recipe Context:
{recipe_context}

Nutrition:
Calories: {nutrition['calories']}
Protein: {nutrition['protein']}
Carbs: {nutrition['carbs']}
Fat: {nutrition['fat']}

Preference Weight: {preference_weight}

Output Format:
Title
Ingredients
Steps
Nutrition Summary
Health Explanation
"""

        # 6. Generate final text
        final_text = LLMService.generate_text(prompt)

        return {
            "recipe_name": recipe["name"],
            "final_text": final_text
        }
