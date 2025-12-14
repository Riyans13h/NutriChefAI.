"""
Data Science Scoring Engine
---------------------------
Implements the mathematical model used to rank recipes.
"""

from app.database import MySQLDatabase


class DataScienceEngine:
    """
    Deterministic recipe scoring engine.
    """

    @staticmethod
    def score_recipe(
        user_ingredients: set,
        recipe_ingredients: set,
        recipe_id: int
    ):
        """
        Computes the final score for a recipe.

        Returns:
            dict with score components or None if invalid
        """

        if not recipe_ingredients:
            return None

        # -------------------------------
        # Set-theoretic ingredient model
        # -------------------------------

        matched = user_ingredients.intersection(recipe_ingredients)
        missing = recipe_ingredients.difference(user_ingredients)

        # Coverage Score
        coverage_score = len(matched) / len(recipe_ingredients)

        # Missing Ingredient Penalty
        penalty_score = -len(missing)

        # -------------------------------
        # Nutrition-based Health Score
        # -------------------------------

        nutrition = MySQLDatabase.execute_query(
            query="""
                SELECT calories, protein, carbs, fat
                FROM nutrition
                WHERE recipe_id = %s
            """,
            params=(recipe_id,),
            fetchone=True
        )

        if not nutrition:
            return None

        calories = nutrition["calories"]
        protein = nutrition["protein"]
        carbs = nutrition["carbs"]
        fat = nutrition["fat"]

        # Balanced diet health score
        # H = 2P + C - F
        health_score = (2 * protein) + carbs - fat

        # -------------------------------
        # Final Weighted Score
        # -------------------------------

        final_score = (
            0.6 * coverage_score +
            0.3 * health_score +
            0.1 * penalty_score
        )

        return {
            "coverage": coverage_score,
            "penalty": penalty_score,
            "health": health_score,
            "final_score": final_score
        }
