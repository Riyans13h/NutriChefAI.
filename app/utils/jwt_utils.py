import jwt
from datetime import datetime, timedelta
from typing import Optional
from flask import current_app


def generate_jwt(user_id: int, expires_in: int = 3600) -> str:
    """
    Generates a JWT token for a user.

    Args:
        user_id (int): Authenticated user ID
        expires_in (int): Token validity in seconds

    Returns:
        str: Encoded JWT token
    """

    payload = {
        "user_id": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token


def decode_jwt(token: str) -> Optional[int]:
    """
    Decodes and validates JWT token.

    Returns:
        user_id if valid, else None
    """

    try:
        decoded = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        return decoded.get("user_id")

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
