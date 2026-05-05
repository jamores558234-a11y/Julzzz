"""Service controller"""
from database.connection import DatabaseConnection


class ServiceController:
    def __init__(self):
        self.db = DatabaseConnection()

    def create_service(self, vehicle_id, mechanic_id, issue_complaint):
        """Create new service"""
        try:
            query = """INSERT INTO services (vehicle_id, mechanic_id, issue_complaint, status) 
                      VALUES (%s, %s, %s, 'Pending')"""
            result = self.db.execute_query(query, (vehicle_id, mechanic_id, issue_complaint))
            return result > 0
        except Exception as e:
            print(f"Create Service Error: {e}")
            return False

    def get_all_services(self):
        """Get all services with details"""
        try:
            query = """SELECT s.*, v.plate_number, v.model, CONCAT(c.last_name, ', ', c.first_name, IF(c.middle_name IS NOT NULL AND c.middle_name != '', CONCAT(' ', c.middle_name), '')) as customer_name, u.full_name as mechanic_name 
                      FROM services s
                      JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                      JOIN customers c ON v.customer_id = c.customer_id
                      LEFT JOIN users u ON s.mechanic_id = u.user_id"""
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get Services Error: {e}")
            return []

    def get_service(self, service_id):
        """Get single service"""
        try:
            query = """SELECT s.*, v.plate_number, v.model, CONCAT(c.last_name, ', ', c.first_name, IF(c.middle_name IS NOT NULL AND c.middle_name != '', CONCAT(' ', c.middle_name), '')) as customer_name, u.full_name as mechanic_name 
                      FROM services s
                      JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                      JOIN customers c ON v.customer_id = c.customer_id
                      LEFT JOIN users u ON s.mechanic_id = u.user_id
                      WHERE s.service_id = %s"""
            result = self.db.execute_query(query, (service_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Get Service Error: {e}")
            return None

    def update_service_status(self, service_id, new_status):
        """Update service status"""
        try:
            current_service = self.get_service(service_id)
            if not current_service:
                return False

            current_status = current_service['status']
            status_order = {'Pending': 0, 'Ongoing': 1, 'Completed': 2}

            # Enforce strict status flow
            if status_order[new_status] <= status_order[current_status]:
                return False

            query = "UPDATE services SET status = %s WHERE service_id = %s"
            result = self.db.execute_query(query, (new_status, service_id))
            return result > 0
        except Exception as e:
            print(f"Update Service Status Error: {e}")
            return False

    def assign_mechanic(self, service_id, mechanic_id):
        """Assign mechanic to service"""
        try:
            query = "UPDATE services SET mechanic_id = %s WHERE service_id = %s"
            result = self.db.execute_query(query, (mechanic_id, service_id))
            return result > 0
        except Exception as e:
            print(f"Assign Mechanic Error: {e}")
            return False

    def can_complete_service(self, service_id):
        """Check if service can be completed"""
        try:
            # Check mechanic assigned
            service = self.get_service(service_id)
            if not service or not service['mechanic_id']:
                return False, "No mechanic assigned"

            # Check repair record exists
            query = "SELECT * FROM repairs WHERE service_id = %s"
            repairs = self.db.execute_query(query, (service_id,))
            if not repairs:
                return False, "No repair record found"

            # Check parts recorded
            query = "SELECT * FROM service_parts WHERE service_id = %s"
            parts = self.db.execute_query(query, (service_id,))
            if not parts:
                return False, "No parts recorded"

            # Check payment
            query = """SELECT b.* FROM billing b 
                      WHERE b.service_id = %s AND b.status = 'Paid'"""
            payment = self.db.execute_query(query, (service_id,))
            if not payment:
                return False, "Service not paid"

            return True, "Service can be completed"
        except Exception as e:
            print(f"Can Complete Service Error: {e}")
            return False, str(e)