import re
from typing import List, Set
from app.models.ingredient_model import IngredientSynonym


class IngredientNormalizer:
    """
    Normalizes ingredients using database-backed synonyms.
    """

    @staticmethod
    def clean(text: str) -> str:
        text = text.lower().strip()
        return re.sub(r"[^a-z\s]", "", text)

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Normalize a single ingredient using DB synonyms.
        """
        cleaned = cls.clean(text)

        synonym = IngredientSynonym.query.filter_by(
            raw_name=cleaned
        ).first()

        return synonym.normalized_name if synonym else cleaned

    @classmethod
    def normalize_list(cls, ingredients: List[str]) -> Set[str]:
        """
        Normalize a list of ingredients.
        """
        return {cls.normalize(ing) for ing in ingredients if ing.strip()}
