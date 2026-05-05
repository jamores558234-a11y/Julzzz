

class Payment:
    def __init__(self, payment_id, billing_id, amount_paid, payment_method):
        self.payment_id = payment_id
        self.billing_id = billing_id
        self.amount_paid = amount_paid
        self.payment_method = payment_method