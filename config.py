"""Application Configuration"""

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'car_aircon_db',
    'port': 3306
}

# Application Settings
APP_TITLE = "Julz Car Air Conditioning Service Management System"
APP_VERSION = "1.0.0"
APP_WIDTH = 1600
APP_HEIGHT = 900

# UI Theme Colors (Modern Professional Palette)
UI_THEME = {
    'primary': '#2563eb',
    'primary_light': '#3b82f6',
    'primary_dark': '#1e40af',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#06b6d4',
    'secondary': '#6b7280',
    'light_bg': '#f8fafc',
    'card_bg': '#ffffff',
    'border': '#e5e7eb',
    'text_primary': '#1f2937',
    'text_secondary': '#6b7280',
    'sidebar': '#1e293b'
}

# Role Settings
ROLES = {
    'ADMIN': 'Admin',
    'STAFF': 'Staff',
    'MECHANIC': 'Mechanic'
}

# Service Status
SERVICE_STATUS = [
    'Pending',
    'Ongoing',
    'Completed'
]

# Low Stock Threshold
LOW_STOCK_THRESHOLD = 5

# Font Settings
FONTS = {
    'title': {'family': 'Segoe UI', 'size': 16, 'weight': 700},
    'heading': {'family': 'Segoe UI', 'size': 14, 'weight': 600},
    'label': {'family': 'Segoe UI', 'size': 12, 'weight': 600},
    'body': {'family': 'Segoe UI', 'size': 12, 'weight': 400},
}