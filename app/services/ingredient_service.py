"""
Ingredient Processing Service
-----------------------------
Responsible for:
- Parsing user input text
- Normalizing ingredient names
- Producing clean ingredient sets for scoring
"""

import re

from app.utils.ingredient_normalizer import normalize_ingredient


class IngredientService:
    """
    Handles ingredient parsing and normalization.
    """

    @staticmethod
    def parse_user_ingredients(raw_text: str):
        """
        Converts raw user ingredient input into a normalized set.

        Example:
            Input:  "Rice, tomato ; Paneer!!"
            Output: {"rice", "tomato", "paneer"}

        Returns:
            set[str]
        """

        if not raw_text:
            return set()

        # Split on commas, semicolons, or newlines
        tokens = re.split(r"[,\n;]+", raw_text.lower())

        normalized_ingredients = set()

        for token in tokens:
            cleaned = normalize_ingredient(token)
            if cleaned:
                normalized_ingredients.add(cleaned)

        return normalized_ingredients
