
"""Inventory controller"""
from database.connection import DatabaseConnection


class InventoryController:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_items(self):
        """Get all inventory items"""
        try:
            query = "SELECT * FROM inventory"
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Get Inventory Error: {e}")
            return []

    def add_item(self, item_name, quantity, unit_price, minimum_threshold=5):
        """Add new inventory item"""
        try:
            query = """INSERT INTO inventory (item_name, quantity_available, unit_price, minimum_threshold) 
                      VALUES (%s, %s, %s, %s)"""
            result = self.db.execute_query(query, (item_name, quantity, unit_price, minimum_threshold))
            return result > 0
        except Exception as e:
            print(f"Add Item Error: {e}")
            return False

    def stock_in(self, item_id, quantity, supplier, total_cost):
        """Add stock in"""
        try:
            # Insert stock in record
            query = """INSERT INTO stock_in (item_id, quantity, supplier, total_cost) 
                      VALUES (%s, %s, %s, %s)"""
            result = self.db.execute_query(query, (item_id, quantity, supplier, total_cost))

            # Update inventory
            if result > 0:
                query = """UPDATE inventory SET quantity_available = quantity_available + %s 
                          WHERE item_id = %s"""
                self.db.execute_query(query, (quantity, item_id))
                return True
            return False
        except Exception as e:
            print(f"Stock In Error: {e}")
            return False

    def stock_out(self, item_id, quantity, reason):
        """Remove stock"""
        try:
            # Check available quantity
            query = "SELECT quantity_available FROM inventory WHERE item_id = %s"
            result = self.db.execute_query(query, (item_id,))

            if not result or result[0]['quantity_available'] < quantity:
                return False, "Insufficient stock"

            # Insert stock out record
            query = """INSERT INTO stock_out (item_id, quantity, reason) 
                      VALUES (%s, %s, %s)"""
            result = self.db.execute_query(query, (item_id, quantity, reason))

            # Update inventory
            if result > 0:
                query = """UPDATE inventory SET quantity_available = quantity_available - %s 
                          WHERE item_id = %s"""
                self.db.execute_query(query, (quantity, item_id))
                return True, "Stock removed successfully"
            return False, "Failed to remove stock"
        except Exception as e:
            print(f"Stock Out Error: {e}")
            return False, str(e)

    def check_low_stock(self):
        """Get items with low stock"""
        try:
            query = """SELECT * FROM inventory 
                      WHERE quantity_available < minimum_threshold"""
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Check Low Stock Error: {e}")
            return []