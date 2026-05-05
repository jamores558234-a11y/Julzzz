"""Customer controller"""
from database.connection import DatabaseConnection


class CustomerController:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_customer(self, first_name, middle_name, last_name, contact, email, address):
        """Add new customer"""
        try:
            query = """INSERT INTO customers (first_name, middle_name, last_name, contact, email, address)
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            result = self.db.execute_query(query, (first_name, middle_name or None, last_name, contact, email or None, address or None))
            return result > 0
        except Exception as e:
            print(f"Add Customer Error: {e}")
            return False

    def get_all_customers(self):
        """Get all customers — returns list of dicts with full_name helper"""
        try:
            query = """SELECT customer_id, first_name, middle_name, last_name, contact, email, address,
                       CONCAT(last_name, ', ', first_name, IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), '')) AS full_name,
                       CONCAT(first_name, IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''), ' ', last_name) AS display_name
                       FROM customers ORDER BY last_name, first_name"""
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get Customers Error: {e}")
            return []

    def search_customers(self, keyword):
        """Search customers by name, contact, or email"""
        try:
            kw = f"%{keyword}%"
            query = """SELECT customer_id, first_name, middle_name, last_name, contact, email, address,
                       CONCAT(last_name, ', ', first_name, IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), '')) AS full_name,
                       CONCAT(first_name, IF(middle_name IS NOT NULL AND middle_name != '', CONCAT(' ', middle_name), ''), ' ', last_name) AS display_name
                       FROM customers
                       WHERE first_name LIKE %s OR middle_name LIKE %s OR last_name LIKE %s
                          OR contact LIKE %s OR email LIKE %s
                       ORDER BY last_name, first_name"""
            return self.db.execute_query(query, (kw, kw, kw, kw, kw))
        except Exception as e:
            print(f"Search Customers Error: {e}")
            return []

    def get_customer(self, customer_id):
        """Get single customer"""
        try:
            query = """SELECT customer_id, first_name, middle_name, last_name, contact, email, address
                       FROM customers WHERE customer_id = %s"""
            result = self.db.execute_query(query, (customer_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Get Customer Error: {e}")
            return None

    def update_customer(self, customer_id, first_name, middle_name, last_name, contact, email, address):
        """Update customer"""
        try:
            query = """UPDATE customers SET first_name=%s, middle_name=%s, last_name=%s,
                       contact=%s, email=%s, address=%s WHERE customer_id=%s"""
            result = self.db.execute_query(query, (first_name, middle_name or None, last_name, contact, email or None, address or None, customer_id))
            return result > 0
        except Exception as e:
            print(f"Update Customer Error: {e}")
            return False

    def delete_customer(self, customer_id):
        """Delete customer"""
        try:
            query = "DELETE FROM customers WHERE customer_id = %s"
            result = self.db.execute_query(query, (customer_id,))
            return result > 0
        except Exception as e:
            print(f"Delete Customer Error: {e}")
            return False