

class Repair:
    def __init__(self, repair_id, service_id, diagnosis_result=None, repair_actions=None):
        self.repair_id = repair_id
        self.service_id = service_id
        self.diagnosis_result = diagnosis_result
        self.repair_actions = repair_actions