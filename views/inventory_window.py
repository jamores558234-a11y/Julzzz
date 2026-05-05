"""Inventory management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QSpinBox, QDoubleSpinBox, QComboBox, QFrame, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.inventory_controller import InventoryController
from views.widgets import SHARED_INPUT_STYLE, SHARED_TABLE_STYLE, btn_style, section_label

SPIN_STYLE = """
    QSpinBox, QDoubleSpinBox {
        padding: 10px 14px;
        border: 1.5px solid #d1d5db;
        border-radius: 8px;
        font-size: 13px;
        background:#f9fafb;
        color:#111827;
        font-family:'Segoe UI',sans-serif;
    }
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1.5px solid #2563eb;
        background:#ffffff;
    }
"""
COMBO_STYLE = """
    QComboBox {
        padding: 10px 14px;
        border: 1.5px solid #d1d5db;
        border-radius: 8px;
        font-size: 13px;
        background:#f9fafb;
        color:#111827;
        font-family:'Segoe UI',sans-serif;
    }
    QComboBox:focus { border:1.5px solid #2563eb; background:#fff; }
    QComboBox QAbstractItemView {
        background:#fff; color:#1f2937;
        selection-background-color:#dbeafe; selection-color:#1e40af;
        border:1px solid #d1d5db; border-radius:6px; padding:4px;
        font-family:'Segoe UI',sans-serif;
    }
"""

class InventoryWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.inventory_controller = InventoryController()
        self.init_ui()
        try: self.load_inventory()
        except Exception as e: print(f"Error loading inventory: {e}")

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
        t = QLabel("📦  Inventory Management")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        hl.addWidget(t)
        sub = QLabel("Track stock levels, record stock-in and stock-out transactions")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        hl.addWidget(sub)
        layout.addWidget(hf)

        # Stock panels side by side
        panels = QHBoxLayout()
        panels.setSpacing(16)
        panels.addWidget(self._build_stockin_panel())
        panels.addWidget(self._build_stockout_panel())
        layout.addLayout(panels)

        # Table
        tbl_lbl = QLabel("Inventory Status")
        tbl_lbl.setStyleSheet("color:#374151;font-size:13px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        layout.addWidget(tbl_lbl)

        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID','Item Name','Available Qty','Min Threshold','Unit Price (₱)','Status'])
        self.table.setColumnHidden(0, True)
        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)
        layout.addWidget(tf)

    def _build_stockin_panel(self):
        f = QFrame()
        f.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        fl = QVBoxLayout(f)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        hdr = QLabel("📥  Stock In")
        hdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(hdr)

        fl.addWidget(section_label("Item"))
        self.stockin_item_combo = QComboBox()
        self.stockin_item_combo.setStyleSheet(COMBO_STYLE)
        self.stockin_item_combo.setMinimumHeight(42)
        try: self._load_items_combo(self.stockin_item_combo)
        except: pass
        fl.addWidget(self.stockin_item_combo)

        row = QHBoxLayout()
        row.setSpacing(12)
        qc = QVBoxLayout()
        qc.addWidget(section_label("Quantity"))
        self.stockin_qty = QSpinBox()
        self.stockin_qty.setMinimum(1)
        self.stockin_qty.setMaximum(99999)
        self.stockin_qty.setStyleSheet(SPIN_STYLE)
        self.stockin_qty.setMinimumHeight(42)
        qc.addWidget(self.stockin_qty)
        row.addLayout(qc)

        cc = QVBoxLayout()
        cc.addWidget(section_label("Total Cost (₱)"))
        self.stockin_cost = QDoubleSpinBox()
        self.stockin_cost.setMinimum(0)
        self.stockin_cost.setMaximum(9999999)
        self.stockin_cost.setStyleSheet(SPIN_STYLE)
        self.stockin_cost.setMinimumHeight(42)
        cc.addWidget(self.stockin_cost)
        row.addLayout(cc)
        fl.addLayout(row)

        fl.addWidget(section_label("Supplier"))
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Supplier name")
        self.supplier_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.supplier_input.setMinimumHeight(42)
        fl.addWidget(self.supplier_input)

        btn = QPushButton("➕  Stock In")
        btn.setStyleSheet(btn_style("#10b981","#059669","#047857"))
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.stock_in)
        fl.addWidget(btn)
        return f

    def _build_stockout_panel(self):
        f = QFrame()
        f.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        fl = QVBoxLayout(f)
        fl.setContentsMargins(20, 16, 20, 16)
        fl.setSpacing(12)

        hdr = QLabel("📤  Stock Out")
        hdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(hdr)

        fl.addWidget(section_label("Item"))
        self.stockout_item_combo = QComboBox()
        self.stockout_item_combo.setStyleSheet(COMBO_STYLE)
        self.stockout_item_combo.setMinimumHeight(42)
        try: self._load_items_combo(self.stockout_item_combo)
        except: pass
        fl.addWidget(self.stockout_item_combo)

        fl.addWidget(section_label("Quantity"))
        self.stockout_qty = QSpinBox()
        self.stockout_qty.setMinimum(1)
        self.stockout_qty.setMaximum(99999)
        self.stockout_qty.setStyleSheet(SPIN_STYLE)
        self.stockout_qty.setMinimumHeight(42)
        fl.addWidget(self.stockout_qty)

        fl.addWidget(section_label("Reason"))
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("Reason for stock out")
        self.reason_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.reason_input.setMinimumHeight(42)
        fl.addWidget(self.reason_input)

        fl.addStretch()

        btn = QPushButton("➖  Stock Out")
        btn.setStyleSheet(btn_style("#ef4444","#dc2626","#b91c1c"))
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.stock_out)
        fl.addWidget(btn)
        return f

    def _load_items_combo(self, combo):
        items = self.inventory_controller.get_all_items()
        if items:
            for item in items:
                combo.addItem(item.get('item_name',''), item.get('item_id'))

    def load_inventory(self):
        try:
            items = self.inventory_controller.get_all_items() or []
            self.table.setRowCount(len(items))
            for row, item in enumerate(items):
                qty = item.get('quantity_available', 0)
                threshold = item.get('minimum_threshold', 0)
                self.table.setItem(row,0,QTableWidgetItem(str(item.get('item_id',''))))
                self.table.setItem(row,1,QTableWidgetItem(item.get('item_name','')))
                self.table.setItem(row,2,QTableWidgetItem(str(qty)))
                self.table.setItem(row,3,QTableWidgetItem(str(threshold)))
                self.table.setItem(row,4,QTableWidgetItem(f"₱{float(item.get('unit_price',0)):,.2f}"))
                status = "⚠  Low Stock" if qty < threshold else "✓  OK"
                si = QTableWidgetItem(status)
                self.table.setItem(row,5,si)
        except Exception as e:
            print(f"Error loading inventory: {e}")

    def stock_in(self):
        try:
            item_id = self.stockin_item_combo.currentData()
            if not item_id:
                QMessageBox.warning(self,"Validation Error","Please select an item.")
                return
            supplier = self.supplier_input.text().strip()
            if not supplier:
                QMessageBox.warning(self,"Validation Error","Please enter the supplier name.")
                return
            if self.inventory_controller.stock_in(item_id, self.stockin_qty.value(), supplier, self.stockin_cost.value()):
                QMessageBox.information(self,"Success","Stock added successfully.")
                self.supplier_input.clear()
                self.stockin_qty.setValue(1)
                self.stockin_cost.setValue(0)
                self.load_inventory()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self,"Error","Failed to add stock.")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))

    def stock_out(self):
        try:
            item_id = self.stockout_item_combo.currentData()
            if not item_id:
                QMessageBox.warning(self,"Validation Error","Please select an item.")
                return
            reason = self.reason_input.text().strip()
            if not reason:
                QMessageBox.warning(self,"Validation Error","Please enter a reason.")
                return
            success, message = self.inventory_controller.stock_out(item_id, self.stockout_qty.value(), reason)
            if success:
                QMessageBox.information(self,"Success",message)
                self.reason_input.clear()
                self.stockout_qty.setValue(1)
                self.load_inventory()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self,"Error",message)
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))