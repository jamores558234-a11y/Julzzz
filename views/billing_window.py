"""Billing management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox,
                             QComboBox, QFrame, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.billing_controller import BillingController
from controllers.service_controller import ServiceController
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from views.widgets import SHARED_TABLE_STYLE, btn_style, section_label

COMBO_STYLE = """
    QComboBox {
        padding: 10px 14px;
        border: 1.5px solid #d1d5db;
        border-radius: 8px;
        font-size: 13px;
        background:#f9fafb;color:#111827;
        font-family:'Segoe UI',sans-serif;
    }
    QComboBox:focus{border:1.5px solid #2563eb;background:#fff;}
    QComboBox QAbstractItemView{
        background:#fff;color:#1f2937;
        selection-background-color:#dbeafe;selection-color:#1e40af;
        border:1px solid #d1d5db;border-radius:6px;padding:4px;
        font-family:'Segoe UI',sans-serif;
    }
"""
SPIN_STYLE = """
    QDoubleSpinBox {
        padding:10px 14px;border:1.5px solid #d1d5db;border-radius:8px;
        font-size:13px;background:#f9fafb;color:#111827;
        font-family:'Segoe UI',sans-serif;
    }
    QDoubleSpinBox:focus{border:1.5px solid #2563eb;background:#fff;}
"""

class BillingWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.billing_controller = BillingController()
        self.service_controller = ServiceController()
        self.db = DatabaseConnection()
        self.init_ui()
        try:
            self.load_billing()
        except Exception as e:
            print(f"Error loading billing: {e}")

    def init_ui(self):
        self.setStyleSheet("background:#f8fafc;font-family:'Segoe UI',sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header Section
        hf = QFrame()
        hf.setStyleSheet("QFrame{background:#fff;border-bottom:2px solid #e2e8f0;}")
        hl = QVBoxLayout(hf)
        hl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("💰  Billing Management")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        hl.addWidget(t)
        sub = QLabel("Create and track billing records for completed services")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        hl.addWidget(sub)
        layout.addWidget(hf)

        # Form Section
        ff = QFrame()
        ff.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        fl = QVBoxLayout(ff)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(14)

        fhdr = QLabel("New Billing")
        fhdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(fhdr)

        row = QHBoxLayout()
        row.setSpacing(14)

        sc = QVBoxLayout()
        sc.addWidget(section_label("Service *"))
        self.service_combo = QComboBox()
        self.service_combo.setStyleSheet(COMBO_STYLE)
        self.service_combo.setMinimumHeight(42)
        try:
            self.load_services_combo()
        except:
            pass
        sc.addWidget(self.service_combo)
        row.addLayout(sc, 2)

        lc = QVBoxLayout()
        lc.addWidget(section_label("Labor Fee (₱)"))
        self.labor_fee_spin = QDoubleSpinBox()
        self.labor_fee_spin.setMinimum(0)
        self.labor_fee_spin.setMaximum(999999)
        self.labor_fee_spin.setValue(500)
        self.labor_fee_spin.setStyleSheet(SPIN_STYLE)
        self.labor_fee_spin.setMinimumHeight(42)
        lc.addWidget(self.labor_fee_spin)
        row.addLayout(lc, 1)

        fl.addLayout(row)
        layout.addWidget(ff)

        # Action Buttons
        br = QHBoxLayout()
        br.setSpacing(10)

        cb = QPushButton("➕  Create Billing")
        cb.setStyleSheet(btn_style("#10b981", "#059669", "#047857"))
        cb.setMinimumHeight(44)
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.clicked.connect(self.create_billing)
        br.addWidget(cb)

        vb = QPushButton("👁  View Details")
        vb.setStyleSheet(btn_style("#3b82f6", "#2563eb", "#1d4ed8"))
        vb.setMinimumHeight(44)
        vb.setCursor(Qt.CursorShape.PointingHandCursor)
        vb.clicked.connect(self.view_billing_details)
        br.addWidget(vb)

        rb = QPushButton("🔄  Refresh")
        rb.setStyleSheet(btn_style("#8b5cf6", "#7c3aed"))
        rb.setMinimumHeight(44)
        rb.setCursor(Qt.CursorShape.PointingHandCursor)
        rb.clicked.connect(self.load_billing)
        br.addWidget(rb)

        br.addStretch()
        layout.addLayout(br)

        # Updated Table Section to match Database View
        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        # Changed column count to 11 to fit all View data
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Service #', 'Vehicle', 'Model', 'Customer',
            'Contact', 'Parts Cost', 'Labor Fee', 'Total', 'Status', 'Date'
        ])

        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive) # Changed for better visibility
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)
        layout.addWidget(tf)

    def load_services_combo(self):
        services = self.service_controller.get_all_services()
        if services:
            for s in services:
                self.service_combo.addItem(
                    f"Service #{s.get('service_id','')}  —  {s.get('plate_number','')}",
                    s.get('service_id'))

    def load_billing(self):
        """Updated to map keys from vw_billing_summary"""
        try:
            billings = self.billing_controller.get_all_billing() or []
            self.table.setRowCount(len(billings))
            for row, b in enumerate(billings):
                # Using .get() to safely pull from the database dictionary
                self.table.setItem(row, 0, QTableWidgetItem(str(b.get('billing_id', ''))))
                self.table.setItem(row, 1, QTableWidgetItem(str(b.get('service_id', ''))))
                self.table.setItem(row, 2, QTableWidgetItem(b.get('plate_number', '')))
                self.table.setItem(row, 3, QTableWidgetItem(b.get('model', '')))
                self.table.setItem(row, 4, QTableWidgetItem(b.get('customer_name', '')))
                self.table.setItem(row, 5, QTableWidgetItem(b.get('contact', '')))
                self.table.setItem(row, 6, QTableWidgetItem(format_currency(b.get('parts_cost', 0))))
                self.table.setItem(row, 7, QTableWidgetItem(format_currency(b.get('labor_fee', 0))))
                self.table.setItem(row, 8, QTableWidgetItem(format_currency(b.get('total_amount', 0))))
                self.table.setItem(row, 9, QTableWidgetItem(b.get('status', '')))

                # Format timestamp to Date string
                created_dt = str(b.get('created_at', ''))[:10]
                self.table.setItem(row, 10, QTableWidgetItem(created_dt))
        except Exception as e:
            print(f"Error loading billing: {e}")

    def create_billing(self):
        """Creates billing. Triggers in MySQL run immediately after the execute_query inside the controller."""
        try:
            service_id = self.service_combo.currentData()
            if not service_id:
                QMessageBox.warning(self, "Validation Error", "Please select a service.")
                return

            labor_fee = self.labor_fee_spin.value()

            # Fetch parts cost directly via query
            result = self.db.execute_query("SELECT SUM(total_price) as total FROM service_parts WHERE service_id = %s", (service_id,))
            parts_cost = float(result[0]['total']) if result and result[0]['total'] else 0.0

            if self.billing_controller.create_billing(service_id, parts_cost, labor_fee):
                QMessageBox.information(self, "Success", "Billing created successfully.")
                self.load_billing() # Refreshes table to show new data + any trigger results
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to create billing. It may already exist.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def view_billing_details(self):
        try:
            row = self.table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a billing record first.")
                return

            billing_id = int(self.table.item(row, 0).text())
            # Note: Since the controller is updated, this b now includes Model, Contact, etc.
            b = self.billing_controller.get_billing(billing_id)
            if b:
                msg = (f"Billing ID:    #{b.get('billing_id', '')}\n"
                       f"Vehicle:       {b.get('plate_number', '')} ({b.get('model', '')})\n"
                       f"Customer:      {b.get('customer_name', '')}\n"
                       f"Contact:       {b.get('contact', '')}\n\n"
                       f"Parts Cost:    {format_currency(b.get('parts_cost', 0))}\n"
                       f"Labor Fee:     {format_currency(b.get('labor_fee', 0))}\n"
                       f"Total Amount:  {format_currency(b.get('total_amount', 0))}\n"
                       f"Status:        {b.get('status', '')}\n")
                QMessageBox.information(self, "Billing Details", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))