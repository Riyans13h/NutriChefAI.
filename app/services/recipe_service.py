"""
Recipe Service
--------------
Responsible for:
- Retrieving recipes from SQL
- Coordinating ingredient parsing
- Running Data Science ranking
"""

from app.database import MySQLDatabase
from app.services.ingredient_service import IngredientService
from app.services.ds_engine import DataScienceEngine


class RecipeService:
    """
    Orchestrates recipe retrieval and ranking.
    """

    @staticmethod
    def get_ranked_recipes(user_ingredients_text: str, meal_type: str):
        """
        Retrieves and ranks recipes for a given meal type.

        Returns:
            list[dict]: ranked recipe metadata
        """

        user_ingredients = IngredientService.parse_user_ingredients(
            raw_text=user_ingredients_text
        )

        if not user_ingredients:
            return []

        # Fetch recipes filtered by meal type
        recipes = MySQLDatabase.execute_query(
            query="""
                SELECT recipe_id, name, time_to_cook
                FROM recipes
                WHERE meal_type = %s
            """,
            params=(meal_type,),
            fetchall=True
        )

        ranked_recipes = []

        for recipe in recipes:
            ingredients = MySQLDatabase.execute_query(
                query="""
                    SELECT i.name
                    FROM recipe_ingredients ri
                    JOIN ingredients i
                    ON ri.ingredient_id = i.ingredient_id
                    WHERE ri.recipe_id = %s
                """,
                params=(recipe["recipe_id"],),
                fetchall=True
            )

            recipe_ingredients = {row["name"] for row in ingredients}

            score_data = DataScienceEngine.score_recipe(
                user_ingredients=user_ingredients,
                recipe_ingredients=recipe_ingredients,
                recipe_id=recipe["recipe_id"]
            )

            if score_data is None:
                continue

            ranked_recipes.append({
                "recipe_id": recipe["recipe_id"],
                "name": recipe["name"],
                "time_to_cook": recipe["time_to_cook"],
                "score": score_data["final_score"]
            })

        ranked_recipes.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return ranked_recipes[:4]
