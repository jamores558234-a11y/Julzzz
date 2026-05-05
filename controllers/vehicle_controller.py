
from database.connection import DatabaseConnection


class VehicleController:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_vehicle(self, customer_id, plate_number, model, type_val, year, color):
        """Add new vehicle"""
        try:
            query = """INSERT INTO vehicles (customer_id, plate_number, model, type, year, color) 
                      VALUES (%s, %s, %s, %s, %s, %s)"""
            result = self.db.execute_query(query, (customer_id, plate_number, model, type_val, year, color))
            return result > 0
        except Exception as e:
            print(f"Add Vehicle Error: {e}")
            return False

    def get_all_vehicles(self):
        """Get all vehicles with customer names"""
        try:
            query = """SELECT v.*, CONCAT(c.last_name, ', ', c.first_name, IF(c.middle_name IS NOT NULL AND c.middle_name != '', CONCAT(' ', c.middle_name), '')) as customer_name FROM vehicles v 
                      JOIN customers c ON v.customer_id = c.customer_id"""
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get Vehicles Error: {e}")
            return []

    def get_customer_vehicles(self, customer_id):
        """Get vehicles for specific customer"""
        try:
            query = "SELECT * FROM vehicles WHERE customer_id = %s"
            return self.db.execute_query(query, (customer_id,))
        except Exception as e:
            print(f"Get Customer Vehicles Error: {e}")
            return []

    def update_vehicle(self, vehicle_id, customer_id, plate_number, model, type_val, year, color):
        """Update vehicle"""
        try:
            query = """UPDATE vehicles SET customer_id=%s, plate_number=%s, model=%s, 
                      type=%s, year=%s, color=%s WHERE vehicle_id=%s"""
            result = self.db.execute_query(query, (customer_id, plate_number, model, type_val, year, color, vehicle_id))
            return result > 0
        except Exception as e:
            print(f"Update Vehicle Error: {e}")
            return False

    def delete_vehicle(self, vehicle_id):
        """Delete vehicle"""
        try:
            query = "DELETE FROM vehicles WHERE vehicle_id = %s"
            result = self.db.execute_query(query, (vehicle_id,))
            return result > 0
        except Exception as e:
            print(f"Delete Vehicle Error: {e}")
            return False