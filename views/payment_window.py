"""Payment management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox,
                             QComboBox, QLineEdit, QFrame, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.payment_controller import PaymentController
from controllers.billing_controller import BillingController
from database.connection import DatabaseConnection
from utils.helpers import format_currency
from views.widgets import SHARED_INPUT_STYLE, SHARED_TABLE_STYLE, btn_style, section_label

COMBO_STYLE = """
    QComboBox {
        padding:10px 14px;border:1.5px solid #d1d5db;border-radius:8px;
        font-size:13px;background:#f9fafb;color:#111827;font-family:'Segoe UI',sans-serif;
    }
    QComboBox:focus{border:1.5px solid #2563eb;background:#fff;}
    QComboBox QAbstractItemView{
        background:#fff;color:#1f2937;selection-background-color:#dbeafe;
        selection-color:#1e40af;border:1px solid #d1d5db;border-radius:6px;padding:4px;
        font-family:'Segoe UI',sans-serif;
    }
"""
SPIN_STYLE = """
    QDoubleSpinBox {
        padding:10px 14px;border:1.5px solid #d1d5db;border-radius:8px;
        font-size:13px;background:#f9fafb;color:#111827;font-family:'Segoe UI',sans-serif;
    }
    QDoubleSpinBox:focus{border:1.5px solid #2563eb;background:#fff;}
"""


class PaymentWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.payment_controller = PaymentController()
        self.billing_controller = BillingController()
        self.db = DatabaseConnection()
        self.init_ui()
        try: self.load_payments()
        except Exception as e: print(f"Error loading payments: {e}")

    def init_ui(self):
        self.setStyleSheet("background:#f8fafc;font-family:'Segoe UI',sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        hf = QFrame()
        hf.setStyleSheet("QFrame{background:#fff;border-bottom:2px solid #e2e8f0;}")
        hl = QVBoxLayout(hf)
        hl.setContentsMargins(16, 12, 16, 12)
        t = QLabel("💳  Payment Management")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        hl.addWidget(t)
        sub = QLabel("Record payments and track billing status")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        hl.addWidget(sub)
        layout.addWidget(hf)

        # Form
        ff = QFrame()
        ff.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        fl = QVBoxLayout(ff)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(14)

        fhdr = QLabel("Record Payment")
        fhdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(fhdr)

        row = QHBoxLayout()
        row.setSpacing(14)

        bc = QVBoxLayout()
        bc.addWidget(section_label("Billing *"))
        self.billing_combo = QComboBox()
        self.billing_combo.setStyleSheet(COMBO_STYLE)
        self.billing_combo.setMinimumHeight(42)
        try: self.load_billing_combo()
        except: pass
        bc.addWidget(self.billing_combo)
        row.addLayout(bc, 2)

        ac = QVBoxLayout()
        ac.addWidget(section_label("Amount Paid (₱)"))
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setMinimum(0)
        self.amount_spin.setMaximum(9999999)
        self.amount_spin.setStyleSheet(SPIN_STYLE)
        self.amount_spin.setMinimumHeight(42)
        ac.addWidget(self.amount_spin)
        row.addLayout(ac, 1)

        mc = QVBoxLayout()
        mc.addWidget(section_label("Payment Method"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(['Cash','Check','Credit Card','Bank Transfer','GCash','Maya'])
        self.method_combo.setStyleSheet(COMBO_STYLE)
        self.method_combo.setMinimumHeight(42)
        mc.addWidget(self.method_combo)
        row.addLayout(mc, 1)

        fl.addLayout(row)

        fl.addWidget(section_label("Notes (optional)"))
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("e.g. Full payment, reference number, etc.")
        self.notes_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.notes_input.setMinimumHeight(42)
        fl.addWidget(self.notes_input)

        layout.addWidget(ff)

        # Buttons
        br = QHBoxLayout()
        br.setSpacing(10)

        rb2 = QPushButton("💾  Record Payment")
        rb2.setStyleSheet(btn_style("#10b981","#059669","#047857"))
        rb2.setMinimumHeight(44)
        rb2.setCursor(Qt.CursorShape.PointingHandCursor)
        rb2.clicked.connect(self.record_payment)
        br.addWidget(rb2)

        refr = QPushButton("🔄  Refresh")
        refr.setStyleSheet(btn_style("#8b5cf6","#7c3aed"))
        refr.setMinimumHeight(44)
        refr.setCursor(Qt.CursorShape.PointingHandCursor)
        refr.clicked.connect(self.load_payments)
        br.addWidget(refr)

        br.addStretch()
        layout.addLayout(br)

        # Table
        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Payment ID','Billing #','Amount Paid','Method','Date','Notes'])
        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)
        layout.addWidget(tf)

    def load_billing_combo(self):
        billings = self.billing_controller.get_all_billing()
        if billings:
            for b in billings:
                if b.get('status') != 'Paid':
                    self.billing_combo.addItem(
                        f"Billing #{b.get('billing_id','')}  —  {format_currency(b.get('total_amount',0))}  [{b.get('status','')}]",
                        b.get('billing_id'))

    def load_payments(self):
        try:
            payments = self.db.execute_query("SELECT * FROM payments ORDER BY payment_date DESC LIMIT 100") or []
            self.table.setRowCount(len(payments))
            for row, p in enumerate(payments):
                self.table.setItem(row,0,QTableWidgetItem(str(p.get('payment_id',''))))
                self.table.setItem(row,1,QTableWidgetItem(str(p.get('billing_id',''))))
                self.table.setItem(row,2,QTableWidgetItem(format_currency(p.get('amount_paid',0))))
                self.table.setItem(row,3,QTableWidgetItem(p.get('payment_method','')))
                self.table.setItem(row,4,QTableWidgetItem(str(p.get('payment_date',''))[:16]))
                self.table.setItem(row,5,QTableWidgetItem(p.get('notes','') or ''))
        except Exception as e:
            print(f"Error loading payments: {e}")

    def record_payment(self):
        try:
            billing_id = self.billing_combo.currentData()
            if not billing_id:
                QMessageBox.warning(self,"Validation Error","Please select a billing record.")
                return
            amount = self.amount_spin.value()
            if amount <= 0:
                QMessageBox.warning(self,"Validation Error","Please enter a valid amount.")
                return
            method = self.method_combo.currentText()
            notes = self.notes_input.text().strip()
            if self.payment_controller.record_payment(billing_id, amount, method, notes):
                QMessageBox.information(self,"Success","Payment recorded successfully.")
                self.amount_spin.setValue(0)
                self.notes_input.clear()
                self.load_payments()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self,"Error","Failed to record payment.")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))