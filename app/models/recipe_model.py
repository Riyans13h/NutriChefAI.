from app.database.mysql import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    cuisine = db.Column(db.String(50))
    prep_time_minutes = db.Column(db.Integer)

    nutrition_id = db.Column(db.Integer, db.ForeignKey("nutrition.id"))

    ingredients = db.relationship(
        "Ingredient",
        secondary="recipe_ingredients",
        backref=db.backref("recipes", lazy=True)
    )

    def __repr__(self):
        return f"<Recipe {self.title}>"
