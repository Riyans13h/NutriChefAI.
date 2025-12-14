"""
Reinforcement Learning Engine
-----------------------------
Implements lightweight feedback-based learning to
adjust recipe preference scores over time.
"""

from app.database import MySQLDatabase
from flask import current_app


class RLEngine:
    """
    Reinforcement learning logic using reward aggregation.
    """

    @staticmethod
    def log_feedback(user_id: int, recipe_id: int, reward: int):
        """
        Logs user feedback into the database.

        reward meaning:
        +1  -> user selected / cooked recipe
         0  -> user ignored recipe
        -1  -> user abandoned recipe
        """

        MySQLDatabase.execute_commit(
            query="""
                INSERT INTO user_feedback (user_id, recipe_id, reward)
                VALUES (%s, %s, %s)
            """,
            params=(user_id, recipe_id, reward)
        )

    @staticmethod
    def get_preference_weight(user_id: int, recipe_id: int):
        """
        Computes a preference weight for a recipe
        based on historical feedback.

        Returns:
            float: preference multiplier
        """

        feedback = MySQLDatabase.execute_query(
            query="""
                SELECT AVG(reward) AS avg_reward
                FROM user_feedback
                WHERE user_id = %s AND recipe_id = %s
            """,
            params=(user_id, recipe_id),
            fetchone=True
        )

        if not feedback or feedback["avg_reward"] is None:
            return 1.0

        learning_rate = current_app.config["RL_LEARNING_RATE"]
        base_weight = 1.0

        # Preference adjustment
        preference_weight = base_weight + (
            learning_rate * feedback["avg_reward"]
        )

        return max(0.5, min(preference_weight, 1.5))
