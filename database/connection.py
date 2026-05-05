"""
Database connection module for MySQL
"""
import mysql.connector
from config import DB_CONFIG
from mysql.connector import Error


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Singleton: only initialize once
        if not hasattr(self, '_initialized'):
            self.connection = None
            self.connect()
            self._initialized = True

    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port']
            )
            if self.connection.is_connected():
                print("Connected to MySQL Database")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None

    def get_connection(self):
        """Get database connection"""
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()

            if self.connection is None:
                print("Failed to establish database connection")
                return [] if query.strip().upper().startswith('SELECT') else 0

            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
        except Error as e:
            print(f"Query Error: {e}")
            return [] if query.strip().upper().startswith('SELECT') else 0
        finally:
            cursor.close()

    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")