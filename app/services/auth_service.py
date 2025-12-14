"""
Authentication Service
----------------------
Responsible for:
- User registration
- Password hashing
- User authentication
"""

from passlib.hash import bcrypt

from app.database import MySQLDatabase


class AuthService:
    """
    Authentication-related business logic.
    """

    @staticmethod
    def register_user(full_name: str, email: str, password: str):
        """
        Registers a new user.

        Returns:
            (bool, str): success flag and message
        """

        if not full_name or not email or not password:
            return False, "All fields are required"

        # Check if user already exists
        existing_user = MySQLDatabase.execute_query(
            query="SELECT user_id FROM users WHERE email = %s",
            params=(email,),
            fetchone=True
        )

        if existing_user:
            return False, "Email already registered"

        password_hash = bcrypt.hash(password)

        MySQLDatabase.execute_commit(
            query="""
                INSERT INTO users (full_name, email, password_hash)
                VALUES (%s, %s, %s)
            """,
            params=(full_name, email, password_hash)
        )

        return True, "User registered successfully"

    @staticmethod
    def authenticate_user(email: str, password: str):
        """
        Authenticates a user.

        Returns:
            dict | None: user record if valid, else None
        """

        if not email or not password:
            return None

        user = MySQLDatabase.execute_query(
            query="""
                SELECT user_id, full_name, email, password_hash
                FROM users
                WHERE email = %s
            """,
            params=(email,),
            fetchone=True
        )

        if not user:
            return None

        if not bcrypt.verify(password, user["password_hash"]):
            return None

        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"]
        }
