

import mysql.connector
from mysql.connector import pooling
from flask import current_app


class MySQLDatabase:
    """
    MySQLDatabase uses connection pooling for efficiency.
    One pool is shared across the application.
    """

    _connection_pool = None

    @classmethod
    def initialize_pool(cls):
        """
        Initializes the MySQL connection pool.
        This should be called once when the app starts.
        """
        if cls._connection_pool is None:
            cls._connection_pool = pooling.MySQLConnectionPool(
                pool_name="nutrichef_pool",
                pool_size=10,
                pool_reset_session=True,
                host=current_app.config["DB_HOST"],
                user=current_app.config["DB_USER"],
                password=current_app.config["DB_PASSWORD"],
                database=current_app.config["DB_NAME"],
                port=current_app.config["DB_PORT"],
                autocommit=True
            )

    @classmethod
    def get_connection(cls):
        """
        Fetches a connection from the pool.
        """
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.get_connection()

    @classmethod
    def execute_query(cls, query, params=None, fetchone=False, fetchall=False):
        """
        Executes a SELECT query safely.

        Args:
            query (str): SQL query
            params (tuple): query parameters
            fetchone (bool): return one row
            fetchall (bool): return all rows
        """
        connection = cls.get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return None
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def execute_commit(cls, query, params=None):
        """
        Executes INSERT, UPDATE, DELETE queries.

        Args:
            query (str): SQL query
            params (tuple): query parameters
        """
        connection = cls.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query, params)
            connection.commit()
        finally:
            cursor.close()
            connection.close()
