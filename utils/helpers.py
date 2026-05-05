
def format_currency(amount):

    return f"₱ {amount:,.2f}"

def format_date(date_obj):

    if date_obj:
        return date_obj.strftime("%Y-%m-%d %H:%M")
    return ""

def get_status_color(status):

    colors = {
        'Pending': '#FFA500',
        'Ongoing': '#4169E1',
        'Completed': '#228B22',
        'Paid': '#228B22',
        'Partial': '#FFA500'
    }
    return colors.get(status, '#000000')