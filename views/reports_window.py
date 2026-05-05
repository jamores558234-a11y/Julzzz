"""Reports window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QComboBox, QFrame, QHeaderView)
from PyQt6.QtCore import Qt
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from views.widgets import SHARED_TABLE_STYLE, btn_style, section_label

COMBO_STYLE = """
    QComboBox {
        padding:10px 14px;border:1.5px solid #d1d5db;border-radius:8px;
        font-size:13px;background:#f9fafb;color:#111827;font-family:'Segoe UI',sans-serif;
    }
    QComboBox:focus{border:1.5px solid #2563eb;background:#fff;}
    QComboBox QAbstractItemView{
        background:#fff;color:#1f2937;selection-background-color:#dbeafe;
        selection-color:#1e40af;border:1px solid #d1d5db;border-radius:6px;
        padding:4px;font-family:'Segoe UI',sans-serif;
    }
"""

class ReportsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.init_ui()
        try: self.generate_report()
        except Exception as e: print(f"Error generating report: {e}")

    def init_ui(self):
        self.setStyleSheet("background:#f8fafc;font-family:'Segoe UI',sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        hf = QFrame()
        hf.setStyleSheet("QFrame{background:#fff;border-bottom:2px solid #e2e8f0;}")
        hl = QVBoxLayout(hf)
        hl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("📈  Reports")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        hl.addWidget(t)
        sub = QLabel("Generate and view system reports")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        hl.addWidget(sub)
        layout.addWidget(hf)

        # Controls
        cf = QFrame()
        cf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        cl = QHBoxLayout(cf)
        cl.setContentsMargins(20, 14, 20, 14)
        cl.setSpacing(14)

        cl.addWidget(section_label("Report Type"))
        self.report_combo = QComboBox()
        self.report_combo.setStyleSheet(COMBO_STYLE)
        self.report_combo.setMinimumHeight(42)
        self.report_combo.setMinimumWidth(260)
        self.report_combo.addItems([
            'Service History',
            'Inventory Status',
            'Payment Transactions',
            'Low Stock Items',
        ])
        self.report_combo.currentTextChanged.connect(self.generate_report)
        cl.addWidget(self.report_combo)

        gen_btn = QPushButton("🔄  Generate")
        gen_btn.setStyleSheet(btn_style("#3b82f6","#2563eb","#1d4ed8"))
        gen_btn.setMinimumHeight(42)
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.clicked.connect(self.generate_report)
        cl.addWidget(gen_btn)

        cl.addStretch()

        self.row_count_lbl = QLabel("")
        self.row_count_lbl.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;")
        cl.addWidget(self.row_count_lbl)

        layout.addWidget(cf)

        # Table
        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)
        layout.addWidget(tf)

    def generate_report(self):
        try:
            t = self.report_combo.currentText()
            if t == 'Service History': self.service_history_report()
            elif t == 'Inventory Status': self.inventory_status_report()
            elif t == 'Payment Transactions': self.payment_transactions_report()
            elif t == 'Low Stock Items': self.low_stock_report()
        except Exception as e:
            print(f"Error generating report: {e}")

    def _set_rows(self, results, headers, cols):
        results = results or []
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(results))
        for row, r in enumerate(results):
            for col, key in enumerate(cols):
                val = r.get(key,'')
                self.table.setItem(row, col, QTableWidgetItem(str(val) if val is not None else ''))
        self.row_count_lbl.setText(f"{len(results)} records")

    def service_history_report(self):
        query = """
        SELECT s.service_id,v.plate_number,
        CONCAT(c.last_name,', ',c.first_name) as customer_name,
        s.issue_complaint,s.status,DATE_FORMAT(s.created_at,'%Y-%m-%d') as date
        FROM services s
        JOIN vehicles v ON s.vehicle_id=v.vehicle_id
        JOIN customers c ON v.customer_id=c.customer_id
        ORDER BY s.created_at DESC LIMIT 200
        """
        r = self.db.execute_query(query) or []
        self._set_rows(r,['Service ID','Vehicle','Customer','Issue','Status','Date'],
                       ['service_id','plate_number','customer_name','issue_complaint','status','date'])

    def inventory_status_report(self):
        query = """
        SELECT item_id,item_name,quantity_available,unit_price,
        quantity_available*unit_price as total_value,minimum_threshold
        FROM inventory ORDER BY item_name
        """
        r = self.db.execute_query(query) or []
        for row in r:
            row['unit_price'] = format_currency(row.get('unit_price',0))
            row['total_value'] = format_currency(row.get('total_value',0))
        self._set_rows(r,['ID','Item','Quantity','Unit Price','Total Value','Threshold'],
                       ['item_id','item_name','quantity_available','unit_price','total_value','minimum_threshold'])

    def payment_transactions_report(self):
        query = """
        SELECT p.payment_id,b.billing_id,p.amount_paid,p.payment_method,
        DATE_FORMAT(p.payment_date,'%Y-%m-%d %H:%i') as pdate,b.total_amount,b.status
        FROM payments p JOIN billing b ON p.billing_id=b.billing_id
        ORDER BY p.payment_date DESC LIMIT 200
        """
        r = self.db.execute_query(query) or []
        for row in r:
            row['amount_paid'] = format_currency(row.get('amount_paid',0))
            row['total_amount'] = format_currency(row.get('total_amount',0))
        self._set_rows(r,['Payment ID','Billing #','Amount Paid','Method','Date','Total Amount','Status'],
                       ['payment_id','billing_id','amount_paid','payment_method','pdate','total_amount','status'])

    def low_stock_report(self):
        query = """
        SELECT item_id,item_name,quantity_available,minimum_threshold,unit_price
        FROM inventory WHERE quantity_available < minimum_threshold ORDER BY quantity_available ASC
        """
        r = self.db.execute_query(query) or []
        for row in r:
            row['unit_price'] = format_currency(row.get('unit_price',0))
        self._set_rows(r,['ID','Item','Available','Threshold','Unit Price'],
                       ['item_id','item_name','quantity_available','minimum_threshold','unit_price'])