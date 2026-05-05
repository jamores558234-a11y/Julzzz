class Customer:
    def __init__(self, customer_id, first_name, middle_name, last_name, contact, email=None, address=None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.middle_name = middle_name or ''
        self.last_name = last_name
        self.contact = contact
        self.email = email
        self.address = address

    @property
    def full_name(self):
        """Last, First Middle format for dropdowns"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return f"{self.last_name}, {' '.join(parts)}"

    @property
    def display_name(self):
        """First Middle Last for tables"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)