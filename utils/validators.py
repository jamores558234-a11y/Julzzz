

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number"""
    import re
    pattern = r'^[0-9]{10,}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def validate_plate_number(plate):
    """Validate plate number format"""
    import re
    pattern = r'^[A-Z]{2,3}-\d{3,4}$'
    return re.match(pattern, plate) is not None

def validate_not_empty(*args):
    """Validate all arguments are not empty"""
    return all(arg and str(arg).strip() for arg in args)

def validate_numeric(value):
    """Validate value is numeric"""
    try:
        float(value)
        return True
    except:
        return False