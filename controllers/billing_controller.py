"""Billing controller"""
from database.connection import DatabaseConnection


class BillingController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_billing(self, service_id, parts_cost, labor_fee):
        """Create billing record"""
        try:
            total_amount = parts_cost + labor_fee
            query = """INSERT INTO billing (service_id, parts_cost, labor_fee, total_amount, status) 
                      VALUES (%s, %s, %s, %s, 'Pending')"""
            result = self.db.execute_query(query, (service_id, parts_cost, labor_fee, total_amount))
            return result > 0
        except Exception as e:
            print(f"Create Billing Error: {e}")
            return False

    def get_billing(self, billing_id):
        """Get billing record"""
        try:
            query = "SELECT * FROM billing WHERE billing_id = %s"
            result = self.db.execute_query(query, (billing_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Get Billing Error: {e}")
            return None

    def get_service_billing(self, service_id):
        """Get billing for service"""
        try:
            query = "SELECT * FROM billing WHERE service_id = %s"
            result = self.db.execute_query(query, (service_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Get Service Billing Error: {e}")
            return None

    def get_all_billing(self):
        """Get all billing records"""
        try:
            query = """SELECT b.*, s.service_id, v.plate_number, CONCAT(c.last_name, ', ', c.first_name, IF(c.middle_name IS NOT NULL AND c.middle_name != '', CONCAT(' ', c.middle_name), '')) as customer_name 
                      FROM billing b
                      JOIN services s ON b.service_id = s.service_id
                      JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                      JOIN customers c ON v.customer_id = c.customer_id"""
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get All Billing Error: {e}")
            return []