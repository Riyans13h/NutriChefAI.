from app.database.mysql import db


class Nutrition(db.Model):
    __tablename__ = "nutrition"

    id = db.Column(db.Integer, primary_key=True)

    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)

    recipe = db.relationship("Recipe", backref="nutrition", uselist=False)

    def __repr__(self):
        return f"<Nutrition {self.calories} kcal>"
