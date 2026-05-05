"""Dashboard window - Live stats that update when data changes"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QMessageBox,
                             QFrame, QGridLayout, QScrollArea)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from views.customer_window import CustomerWindow
from views.vehicle_window import VehicleWindow
from views.service_window import ServiceWindow
from views.inventory_window import InventoryWindow
from views.billing_window import BillingWindow
from views.payment_window import PaymentWindow
from views.reports_window import ReportsWindow




class DashboardWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user

        # Stat value labels (populated in create_dashboard_page)
        self.stat_labels = {}

        self.init_ui()
        self.setWindowTitle("Julz Car AC Service Management System")
        self.showMaximized()

        # Initial stats load
        self.refresh_stats()

    def init_ui(self):
        """Initialize dashboard UI"""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        self.stacked_widget = QStackedWidget()
        self.init_pages()
        main_layout.addWidget(self.stacked_widget, 1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e293b;
            }
            QPushButton {
                background-color: #1e293b;
                color: #e2e8f0;
                border: none;
                padding: 16px 20px;
                text-align: left;
                font-weight: 600;
                border-left: 4px solid transparent;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-left: 4px solid #3b82f6;
            }
            QPushButton:pressed {
                background-color: #0f172a;
                border-left: 4px solid #2563eb;
            }
            QLabel {
                color: #e2e8f0;
                padding: 15px;
                font-weight: 700;
                font-size: 13px;
            }
        """)
        sidebar.setMinimumWidth(240)
        sidebar.setMaximumWidth(260)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("JULZ CAR AC")
        header.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            background-color: #0f172a;
            color: #3b82f6;
            padding: 20px 15px;
            font-weight: 700;
            font-size: 14px;
            border-bottom: 1px solid #334155;
        """)
        layout.addWidget(header)

        user_section = QFrame()
        user_section.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border-bottom: 1px solid #334155;
            }
        """)
        user_layout = QVBoxLayout(user_section)
        user_layout.setContentsMargins(15, 15, 15, 15)
        user_layout.setSpacing(8)

        user_label = QLabel(f"👤 {self.user['full_name']}")
        user_label.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 12px;")
        user_layout.addWidget(user_label)

        role_label = QLabel(f"📋 {self.user['role']}")
        role_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        user_layout.addWidget(role_label)

        layout.addWidget(user_section)

        divider = QLabel("━" * 20)
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setStyleSheet("color: #334155; padding: 10px;")
        layout.addWidget(divider)

        menu_items = [
            ("📊 Dashboard", 0),
            ("👥 Customers", 1),
            ("🚗 Vehicles", 2),
            ("🔧 Services", 3),
            ("📦 Inventory", 4),
            ("💰 Billing", 5),
            ("💳 Payments", 6),
            ("📈 Reports", 7),
        ]

        for label, page_idx in menu_items:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, idx=page_idx: self.stacked_widget.setCurrentIndex(idx))
            layout.addWidget(btn)

        layout.addStretch()

        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f1d1d;
                color: white;
                padding: 14px;
                border: none;
                font-weight: 600;
                border-left: 4px solid #7f1d1d;
            }
            QPushButton:hover {
                background-color: #b91c1c;
                border-left: 4px solid #dc2626;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

        sidebar.setLayout(layout)
        return sidebar

    def init_pages(self):
        """Initialize all pages and connect data_changed signals"""
        dashboard = self.create_dashboard_page()
        self.stacked_widget.addWidget(dashboard)

        self.customer_window = CustomerWindow()
        self.vehicle_window = VehicleWindow()
        self.service_window = ServiceWindow()
        self.inventory_window = InventoryWindow()
        self.billing_window = BillingWindow()
        self.payment_window = PaymentWindow()

        self.stacked_widget.addWidget(self.customer_window)
        self.stacked_widget.addWidget(self.vehicle_window)
        self.stacked_widget.addWidget(self.service_window)
        self.stacked_widget.addWidget(self.inventory_window)
        self.stacked_widget.addWidget(self.billing_window)
        self.stacked_widget.addWidget(self.payment_window)
        self.stacked_widget.addWidget(ReportsWindow())

        # Connect all data_changed signals to refresh_stats
        self.customer_window.data_changed.connect(self.refresh_stats)
        self.vehicle_window.data_changed.connect(self.refresh_stats)

        # When a customer is added/updated/deleted, reload vehicle combo instantly
        self.customer_window.data_changed.connect(
            self.vehicle_window._reload_customer_combo)
        self.service_window.data_changed.connect(self.refresh_stats)
        self.inventory_window.data_changed.connect(self.refresh_stats)
        self.billing_window.data_changed.connect(self.refresh_stats)
        self.payment_window.data_changed.connect(self.refresh_stats)

    def create_dashboard_page(self):
        """Create the dashboard page with live statistics"""
        dashboard = QWidget()
        dashboard.setStyleSheet("background-color: #f8fafc;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: #f8fafc; border: none; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8fafc;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Welcome banner
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563eb, stop:1 #1e40af);
                border-radius: 12px;
            }
        """)
        welcome_frame.setMinimumHeight(120)
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(30, 20, 30, 20)

        welcome_title = QLabel(f"Welcome back, {self.user.get('full_name', 'User')}! 👋")
        welcome_title.setStyleSheet("color: white; font-size: 32px; font-weight: 700;")
        welcome_layout.addWidget(welcome_title)

        welcome_subtitle = QLabel(f"Role: {self.user.get('role', 'Staff')} | Julz Car AC Service Management")
        welcome_subtitle.setStyleSheet("color: #dbeafe; font-size: 14px;")
        welcome_layout.addWidget(welcome_subtitle)

        main_layout.addWidget(welcome_frame)

        # Stats section label
        stats_label = QLabel("📊 Live Statistics")
        stats_label.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: 700;
            margin-top: 10px;
        """)
        main_layout.addWidget(stats_label)

        # Stats grid — 3 columns, 2 rows = 6 cards
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)

        stat_definitions = [
            ("total_customers",   "👥 Total Customers",      "#dbeafe", "#1e40af"),
            ("total_vehicles",    "🚗 Total Vehicles",       "#e0f2fe", "#0369a1"),
            ("active_services",   "🔧 Active Services",      "#dcfce7", "#15803d"),
            ("completed_services","✅ Completed Services",   "#fce7f3", "#be185d"),
            ("total_inventory",   "📦 Inventory Items",      "#fef3c7", "#92400e"),
            ("total_revenue",     "💰 Total Revenue (₱)",    "#ede9fe", "#6d28d9"),
        ]

        for idx, (key, title, bg_color, text_color) in enumerate(stat_definitions):
            card, value_label = self.create_stat_card(title, "—", bg_color, text_color)
            self.stat_labels[key] = value_label
            stats_grid.addWidget(card, idx // 3, idx % 3)

        main_layout.addLayout(stats_grid)

        # Quick Actions
        actions_label = QLabel("⚡ Quick Actions")
        actions_label.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: 700;
            margin-top: 10px;
        """)
        main_layout.addWidget(actions_label)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)

        action_buttons = [
            ("👤 Add Customer",   "#3b82f6", 1),
            ("🚗 Add Vehicle",    "#0ea5e9", 2),
            ("🔧 New Service",    "#10b981", 3),
            ("💰 Process Billing","#f59e0b", 5),
            ("📈 View Reports",   "#8b5cf6", 7),
        ]

        for action_title, color, page_idx in action_buttons:
            action_btn = QPushButton(action_title)
            action_btn.setMinimumHeight(60)
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {color}cc;
                }}
            """)
            action_btn.clicked.connect(lambda checked, idx=page_idx: self.stacked_widget.setCurrentIndex(idx))
            actions_layout.addWidget(action_btn)

        main_layout.addLayout(actions_layout)
        main_layout.addStretch()

        scroll.setWidget(content_widget)

        dashboard_layout = QVBoxLayout(dashboard)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.addWidget(scroll)

        return dashboard

    def refresh_stats(self):
        """Fetch live counts using the same controller instances as sub-windows"""
        try:
            customers = self.customer_window.controller.get_all_customers()
            self.stat_labels["total_customers"].setText(str(len(customers)))
        except Exception as e:
            print(f"refresh_stats customers error: {e}")
            self.stat_labels["total_customers"].setText("0")

        try:
            vehicles = self.vehicle_window.vehicle_controller.get_all_vehicles()
            self.stat_labels["total_vehicles"].setText(str(len(vehicles)))
        except Exception as e:
            print(f"refresh_stats vehicles error: {e}")
            self.stat_labels["total_vehicles"].setText("0")

        try:
            services = self.service_window.service_controller.get_all_services()
            active = sum(1 for s in services if s.get("status") in ("Pending", "Ongoing"))
            completed = sum(1 for s in services if s.get("status") == "Completed")
            self.stat_labels["active_services"].setText(str(active))
            self.stat_labels["completed_services"].setText(str(completed))
        except Exception as e:
            print(f"refresh_stats services error: {e}")
            self.stat_labels["active_services"].setText("0")
            self.stat_labels["completed_services"].setText("0")

        try:
            items = self.inventory_window.inventory_controller.get_all_items()
            self.stat_labels["total_inventory"].setText(str(len(items)))
        except Exception as e:
            print(f"refresh_stats inventory error: {e}")
            self.stat_labels["total_inventory"].setText("0")

        try:
            billings = self.billing_window.billing_controller.get_all_billing()
            revenue = sum(
                float(b.get("total_amount", 0) or 0)
                for b in billings
                if b.get("status") == "Paid"
            )
            self.stat_labels["total_revenue"].setText(f"{revenue:,.2f}")
        except Exception as e:
            print(f"refresh_stats billing error: {e}")
            self.stat_labels["total_revenue"].setText("0.00")

    def create_stat_card(self, title, value, bg_color, text_color):
        """Create a statistics card; returns (card, value_label)"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 1px solid {text_color}33;
            }}
        """)
        card.setMinimumHeight(130)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: 600;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {text_color}; font-size: 42px; font-weight: 700;")
        layout.addWidget(value_label)

        return card, value_label

    def handle_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
            self.close()