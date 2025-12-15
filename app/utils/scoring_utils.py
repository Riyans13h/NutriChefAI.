from typing import Set, Dict


# ---------------- INGREDIENT MATCHING ----------------

def ingredient_coverage(
    user_ingredients: Set[str],
    recipe_ingredients: Set[str]
) -> Dict[str, object]:
    """
    Computes ingredient match, missing ingredients,
    and coverage score using set theory.
    """

    matched = user_ingredients.intersection(recipe_ingredients)
    missing = recipe_ingredients.difference(user_ingredients)

    coverage = len(matched) / len(recipe_ingredients) if recipe_ingredients else 0.0
    penalty = -len(missing)

    return {
        "matched": matched,
        "missing": missing,
        "coverage": round(coverage, 2),
        "penalty": penalty
    }


# ---------------- NUTRITION SCORING ----------------

def nutrition_health_score(
    nutrition: Dict[str, float],
    goal: str
) -> float:
    """
    Computes health score based on user's goal.

    nutrition keys:
    calories, protein, fat, carbohydrates
    """

    protein = nutrition.get("protein", 0.0)
    fat = nutrition.get("fat", 0.0)
    carbs = nutrition.get("carbohydrates", 0.0)

    if goal == "weight_loss":
        # Higher protein, lower fat & carbs
        score = (2 * protein) - fat - (0.5 * carbs)

    elif goal == "muscle_gain":
        # Strong emphasis on protein
        score = (3 * protein) + (0.5 * carbs) - (0.2 * fat)

    else:  # balanced
        score = (2 * protein) + carbs - fat

    return round(score, 2)


# ---------------- FINAL RANKING ----------------

def final_recipe_score(
    coverage: float,
    health_score: float,
    penalty: int
) -> float:
    """
    Computes final ranking score.
    """

    final_score = (
        (0.6 * coverage) +
        (0.3 * health_score) +
        (0.1 * penalty)
    )

    return round(final_score, 2)
