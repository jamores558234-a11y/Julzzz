"""Authentication controller"""
from database.connection import DatabaseConnection
import hashlib


class AuthController:
    def __init__(self):
        self.db = DatabaseConnection()

    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        try:
            query = "SELECT user_id, username, role, full_name FROM users WHERE username = %s AND password = %s"
            result = self.db.execute_query(query, (username, password))

            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            print(f"Authentication Error: {e}")
            return None

    def create_user(self, username, password, role, full_name, contact):
        """Create new user"""
        try:
            query = """INSERT INTO users (username, password, role, full_name, contact) 
                      VALUES (%s, %s, %s, %s, %s)"""
            result = self.db.execute_query(query, (username, password, role, full_name, contact))
            return result > 0
        except Exception as e:
            print(f"Create User Error: {e}")
            return False