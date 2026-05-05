
class InventoryItem:
    def __init__(self, item_id, item_name, quantity_available, unit_price, minimum_threshold=5):
        self.item_id = item_id
        self.item_name = item_name
        self.quantity_available = quantity_available
        self.unit_price = unit_price
        self.minimum_threshold = minimum_threshold