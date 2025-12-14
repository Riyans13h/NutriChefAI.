from app.database.mysql import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)

    rating = db.Column(db.Integer)  # e.g., 1–5
    liked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipe = db.relationship("Recipe", backref="feedbacks")

    def __repr__(self):
        return f"<Feedback user={self.user_id} recipe={self.recipe_id}>"
