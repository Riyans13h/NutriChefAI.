"""
Meal and Recipe Routes
----------------------
Handles:
- User dashboard
- Ingredient input
- Recipe recommendation flow
- Final personalized recipe generation
"""

from flask import Blueprint, render_template, request, redirect, url_for, session

from app.services.recipe_service import RecipeService
from app.services.rag_service import RAGService

meal_bp = Blueprint("meal", __name__, url_prefix="/meal")


def login_required():
    """
    Simple login guard.
    """
    if "user_id" not in session:
        return False
    return True


@meal_bp.route("/dashboard", methods=["GET"])
def dashboard():
    """
    User dashboard page.
    """
    if not login_required():
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name")
    )


@meal_bp.route("/ingredients", methods=["GET", "POST"])
def ingredients():
    """
    Ingredient input page.
    """
    if not login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        meal_type = request.form.get("meal_type")
        ingredients_text = request.form.get("ingredients")

        recipe_list = RecipeService.get_ranked_recipes(
            user_ingredients_text=ingredients_text,
            meal_type=meal_type
        )

        return render_template(
            "recipe_options.html",
            recipe_list=recipe_list
        )

    return render_template("ingredients.html")


@meal_bp.route("/final", methods=["POST"])
def final_recipe():
    """
    Generates the final personalized recipe using RAG + LLM.
    """
    if not login_required():
        return redirect(url_for("auth.login"))

    recipe_id = request.form.get("recipe_id")

    if not recipe_id:
        return redirect(url_for("meal.dashboard"))

    final_output = RAGService.generate_final_recipe(
        recipe_id=int(recipe_id),
        user_id=session.get("user_id")
    )

    return render_template(
        "final_recipe.html",
        recipe=final_output
    )
