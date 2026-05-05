

class Vehicle:
    def __init__(self, vehicle_id, customer_id, plate_number, model, type_val, year=None, color=None):
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.plate_number = plate_number
        self.model = model
        self.type = type_val
        self.year = year
        self.color = color