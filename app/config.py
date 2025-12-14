"""
Application Configuration Module
--------------------------------
Responsible for:
- Loading environment variables
- Centralizing app configuration
- Providing a single source of truth for settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.
    """

    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET", "dev_secret_key")

    # MySQL Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "nutrichef")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # ChromaDB
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "ai_engine/vector_store/chroma_db")

    # Security
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", 24))

    # Reinforcement Learning
    RL_LEARNING_RATE = float(os.getenv("RL_LEARNING_RATE", 0.1))
    RL_DISCOUNT_FACTOR = float(os.getenv("RL_DISCOUNT_FACTOR", 0.9))
    RL_WEIGHT = float(os.getenv("RL_WEIGHT", 0.05))


def init_app(app):
    """
    Attach configuration to Flask app.
    """
    app.config.from_object(Config)
