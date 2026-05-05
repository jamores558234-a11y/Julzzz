

class Billing:
    def __init__(self, billing_id, service_id, parts_cost, labor_fee, status='Pending'):
        self.billing_id = billing_id
        self.service_id = service_id
        self.parts_cost = parts_cost
        self.labor_fee = labor_fee
        self.total_amount = parts_cost + labor_fee
        self.status = status