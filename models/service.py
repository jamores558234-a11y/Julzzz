

class Service:
    def __init__(self, service_id, vehicle_id, issue_complaint, status='Pending', mechanic_id=None):
        self.service_id = service_id
        self.vehicle_id = vehicle_id
        self.mechanic_id = mechanic_id
        self.issue_complaint = issue_complaint
        self.status = status