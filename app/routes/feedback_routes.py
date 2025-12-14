"""
Feedback Routes
---------------
Handles user interaction feedback for reinforcement learning.
"""

from flask import Blueprint, request, session, redirect, url_for

from app.services.rl_engine import RLEngine

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")


def login_required():
    """
    Simple login guard.
    """
    return "user_id" in session


@feedback_bp.route("/log", methods=["POST"])
def log_feedback():
    """
    Logs implicit user feedback.

    Expected form data:
    - recipe_id
    - reward  (1 = selected, 0 = ignored, -1 = abandoned)
    """
    if not login_required():
        return redirect(url_for("auth.login"))

    recipe_id = request.form.get("recipe_id")
    reward = request.form.get("reward")

    if recipe_id is None or reward is None:
        return redirect(url_for("meal.dashboard"))

    RLEngine.log_feedback(
        user_id=session.get("user_id"),
        recipe_id=int(recipe_id),
        reward=int(reward)
    )

    return redirect(url_for("meal.dashboard"))
