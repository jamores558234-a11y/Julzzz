
from database.connection import DatabaseConnection

class BillingController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_billing(self, service_id, parts_cost, labor_fee):

        try:
            total_amount = parts_cost + labor_fee
            query = """INSERT INTO billing (service_id, parts_cost, labor_fee, total_amount, status) 
                      VALUES (%s, %s, %s, %s, 'Pending')"""
            result = self.db.execute_query(query, (service_id, parts_cost, labor_fee, total_amount))
            return result > 0
        except Exception as e:
            print(f"Create Billing Error: {e}")
            return False

    def get_all_billing(self):

        try:
            query = "SELECT * FROM vw_billing_summary ORDER BY created_at DESC"
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get All Billing Error: {e}")
            return []

    def get_billing(self, billing_id):
        try:
            query = "SELECT * FROM vw_billing_summary WHERE billing_id = %s"
            result = self.db.execute_query(query, (billing_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Get Billing Error: {e}")
            return None