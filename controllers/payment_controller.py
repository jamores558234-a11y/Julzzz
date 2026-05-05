"""Payment controller"""
from database.connection import DatabaseConnection


class PaymentController:
    def __init__(self):
        self.db = DatabaseConnection()

    def record_payment(self, billing_id, amount_paid, payment_method, notes=None):
        """Record payment"""
        try:
            query = """INSERT INTO payments (billing_id, amount_paid, payment_method, notes) 
                      VALUES (%s, %s, %s, %s)"""
            result = self.db.execute_query(query, (billing_id, amount_paid, payment_method, notes))

            if result > 0:
                self.update_billing_status(billing_id)
                return True
            return False
        except Exception as e:
            print(f"Record Payment Error: {e}")
            return False

    def update_billing_status(self, billing_id):
        """Update billing status based on payments"""
        try:
            # Get billing info
            query = "SELECT total_amount FROM billing WHERE billing_id = %s"
            billing = self.db.execute_query(query, (billing_id,))

            if not billing:
                return False

            total_amount = billing[0]['total_amount']

            # Get total paid
            query = "SELECT SUM(amount_paid) as total_paid FROM payments WHERE billing_id = %s"
            payment = self.db.execute_query(query, (billing_id,))

            total_paid = payment[0]['total_paid'] if payment and payment[0]['total_paid'] else 0

            # Determine status
            if total_paid >= total_amount:
                status = 'Paid'
            elif total_paid > 0:
                status = 'Partial'
            else:
                status = 'Pending'

            # Update status
            query = "UPDATE billing SET status = %s WHERE billing_id = %s"
            self.db.execute_query(query, (status, billing_id))

            return True
        except Exception as e:
            print(f"Update Billing Status Error: {e}")
            return False

    def get_payments(self, billing_id):
        """Get payments for billing"""
        try:
            query = "SELECT * FROM payments WHERE billing_id = %s"
            return self.db.execute_query(query, (billing_id,))
        except Exception as e:
            print(f"Get Payments Error: {e}")
            return []