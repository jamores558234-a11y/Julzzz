"""Customer management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFrame, QHeaderView, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.customer_controller import CustomerController
from utils.validators import validate_not_empty, validate_email, validate_phone
from views.widgets import (SHARED_INPUT_STYLE, SHARED_TABLE_STYLE,
                           btn_style, section_label)


class CustomerWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.controller = CustomerController()
        self._selected_customer_id = None
        self.init_ui()
        self.load_customers()

    # ── UI Setup ───────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setStyleSheet("background-color: #f8fafc; font-family: 'Segoe UI', sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(10)

        layout.addWidget(self._build_header())
        layout.addWidget(self._build_search_bar())
        layout.addWidget(self._build_form())
        layout.addLayout(self._build_buttons())
        layout.addWidget(self._build_table())

    def _build_header(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background:#ffffff; border-bottom:2px solid #e2e8f0; border-radius:0; }")
        h = QVBoxLayout(frame)
        h.setContentsMargins(16, 8, 16, 8)
        t = QLabel("👥  Customer Management")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        h.addWidget(t)
        sub = QLabel("Add, search, update, and delete customer records")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        h.addWidget(sub)
        return frame

    def _build_search_bar(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:4px;}")
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(10)

        lbl = QLabel("🔍")
        lbl.setStyleSheet("font-size:16px;")
        row.addWidget(lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, contact, or email…")
        self.search_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._on_search)
        row.addWidget(self.search_input)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(btn_style("#6b7280", "#4b5563"))
        clear_btn.setFixedHeight(40)
        clear_btn.clicked.connect(self._clear_search)
        row.addWidget(clear_btn)

        return frame

    def _build_form(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;padding:6px;}")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(8)

        hdr = QLabel("Customer Details")
        hdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(hdr)

        # Row 1: First | Middle | Last
        name_row = QHBoxLayout()
        name_row.setSpacing(14)

        fn_col = QVBoxLayout()
        fn_col.addWidget(section_label("First Name *"))
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Juan")
        self.first_name_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.first_name_input.setMinimumHeight(36)
        fn_col.addWidget(self.first_name_input)
        name_row.addLayout(fn_col)

        mn_col = QVBoxLayout()
        mn_col.addWidget(section_label("Middle Name"))
        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText("Reyes (optional)")
        self.middle_name_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.middle_name_input.setMinimumHeight(36)
        mn_col.addWidget(self.middle_name_input)
        name_row.addLayout(mn_col)

        ln_col = QVBoxLayout()
        ln_col.addWidget(section_label("Last Name *"))
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("dela Cruz")
        self.last_name_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.last_name_input.setMinimumHeight(36)
        ln_col.addWidget(self.last_name_input)
        name_row.addLayout(ln_col)

        fl.addLayout(name_row)

        # Row 2: Contact | Email
        contact_row = QHBoxLayout()
        contact_row.setSpacing(14)

        ct_col = QVBoxLayout()
        ct_col.addWidget(section_label("Contact Number *"))
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("09XXXXXXXXX")
        self.contact_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.contact_input.setMinimumHeight(36)
        ct_col.addWidget(self.contact_input)
        contact_row.addLayout(ct_col)

        em_col = QVBoxLayout()
        em_col.addWidget(section_label("Email Address"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com (optional)")
        self.email_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.email_input.setMinimumHeight(36)
        em_col.addWidget(self.email_input)
        contact_row.addLayout(em_col)

        fl.addLayout(contact_row)

        # Row 3: Address (full width)
        fl.addWidget(section_label("Address"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Street, Barangay, City")
        self.address_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.address_input.setMinimumHeight(36)
        fl.addWidget(self.address_input)

        return frame

    def _build_buttons(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        self.add_btn = QPushButton("➕  Add Customer")
        self.add_btn.setStyleSheet(btn_style("#10b981", "#059669", "#047857"))
        self.add_btn.setMinimumHeight(38)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_customer)
        row.addWidget(self.add_btn)

        self.update_btn = QPushButton("✏️  Update")
        self.update_btn.setStyleSheet(btn_style("#3b82f6", "#2563eb", "#1d4ed8"))
        self.update_btn.setMinimumHeight(38)
        self.update_btn.setEnabled(False)
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.clicked.connect(self.update_customer)
        row.addWidget(self.update_btn)

        self.delete_btn = QPushButton("🗑️  Delete")
        self.delete_btn.setStyleSheet(btn_style("#ef4444", "#dc2626", "#b91c1c"))
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setEnabled(False)   # Disabled until a record is selected
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self.delete_customer)
        row.addWidget(self.delete_btn)

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(btn_style("#8b5cf6", "#7c3aed"))
        refresh_btn.setMinimumHeight(38)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self._clear_search)
        row.addWidget(refresh_btn)

        clear_form_btn = QPushButton("✖  Clear Form")
        clear_form_btn.setStyleSheet(btn_style("#6b7280", "#4b5563"))
        clear_form_btn.setMinimumHeight(38)
        clear_form_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_form_btn.clicked.connect(self._reset_form)
        row.addWidget(clear_form_btn)

        row.addStretch()

        # Selection status badge
        self.selection_lbl = QLabel("No record selected")
        self.selection_lbl.setStyleSheet("""
            color:#6b7280; font-size:12px; font-family:'Segoe UI',sans-serif;
            background:#f3f4f6; border-radius:6px; padding:6px 12px;
        """)
        row.addWidget(self.selection_lbl)

        return row

    def _build_table(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(frame)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Last Name', 'First Name', 'Contact', 'Email', 'Address'])
        self.table.setColumnHidden(0, True)
        self.table.clicked.connect(self.on_row_clicked)
        self.table.setStyleSheet(SHARED_TABLE_STYLE)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        tl.addWidget(self.table)

        return frame

    # ── Data ──────────────────────────────────────────────────────────────────

    def load_customers(self, customers=None):
        if customers is None:
            try:
                customers = self.controller.get_all_customers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load customers: {e}")
                return

        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(c['customer_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(c['last_name']))
            self.table.setItem(row, 2, QTableWidgetItem(c['first_name'] + (' ' + c['middle_name'] if c.get('middle_name') else '')))
            self.table.setItem(row, 3, QTableWidgetItem(c['contact']))
            self.table.setItem(row, 4, QTableWidgetItem(c.get('email') or ''))
            self.table.setItem(row, 5, QTableWidgetItem(c.get('address') or ''))

    def _on_search(self, text):
        if text.strip():
            results = self.controller.search_customers(text.strip())
        else:
            results = self.controller.get_all_customers()
        self.load_customers(results)
        self._reset_selection()

    def _clear_search(self):
        self.search_input.clear()
        self.load_customers()
        self._reset_selection()

    # ── Row click → populate form + enable delete ──────────────────────────────

    def on_row_clicked(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self._selected_customer_id = int(self.table.item(row, 0).text())
        last = self.table.item(row, 1).text()
        first_mid = self.table.item(row, 2).text().split(' ', 1)
        first = first_mid[0]
        mid = first_mid[1] if len(first_mid) > 1 else ''

        self.first_name_input.setText(first)
        self.middle_name_input.setText(mid)
        self.last_name_input.setText(last)
        self.contact_input.setText(self.table.item(row, 3).text())
        self.email_input.setText(self.table.item(row, 4).text())
        self.address_input.setText(self.table.item(row, 5).text())

        self.delete_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        full = f"{last}, {first}{' ' + mid if mid else ''}"
        self.selection_lbl.setText(f"Selected: {full}")
        self.selection_lbl.setStyleSheet("""
            color:#1d4ed8; font-size:12px; font-family:'Segoe UI',sans-serif;
            background:#dbeafe; border-radius:6px; padding:6px 12px;
            font-weight:600;
        """)

    def _reset_selection(self):
        self._selected_customer_id = None
        self.delete_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.selection_lbl.setText("No record selected")
        self.selection_lbl.setStyleSheet("""
            color:#6b7280; font-size:12px; font-family:'Segoe UI',sans-serif;
            background:#f3f4f6; border-radius:6px; padding:6px 12px;
        """)

    def _reset_form(self):
        self.first_name_input.clear()
        self.middle_name_input.clear()
        self.last_name_input.clear()
        self.contact_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self._reset_selection()
        self.table.clearSelection()

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _collect_form(self):
        return (
            self.first_name_input.text().strip(),
            self.middle_name_input.text().strip(),
            self.last_name_input.text().strip(),
            self.contact_input.text().strip(),
            self.email_input.text().strip(),
            self.address_input.text().strip(),
        )

    def add_customer(self):
        first, middle, last, contact, email, address = self._collect_form()
        if not first or not last or not contact:
            QMessageBox.warning(self, "Validation Error", "First name, last name, and contact are required.")
            return
        if email and not validate_email(email):
            QMessageBox.warning(self, "Validation Error", "Invalid email format.")
            return
        if not validate_phone(contact):
            QMessageBox.warning(self, "Validation Error", "Invalid contact number.")
            return
        if self.controller.add_customer(first, middle, last, contact, email, address):
            QMessageBox.information(self, "Success", "Customer added successfully.")
            self._reset_form()
            self.load_customers()
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Error", "Failed to add customer.")

    def update_customer(self):
        if not self._selected_customer_id:
            QMessageBox.warning(self, "Selection Error", "Please search and select a customer first.")
            return
        first, middle, last, contact, email, address = self._collect_form()
        if not first or not last or not contact:
            QMessageBox.warning(self, "Validation Error", "First name, last name, and contact are required.")
            return
        if self.controller.update_customer(self._selected_customer_id, first, middle, last, contact, email, address):
            QMessageBox.information(self, "Success", "Customer updated successfully.")
            self._reset_form()
            self.load_customers()
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Error", "Failed to update customer.")

    def delete_customer(self):
        """Search-before-delete: delete button only enabled after row selection"""
        if not self._selected_customer_id:
            QMessageBox.warning(self, "Selection Error",
                "You must search and select a customer record before deleting.")
            return

        row = self.table.currentRow()
        name = f"{self.table.item(row, 1).text()}, {self.table.item(row, 2).text()}"

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete:\n\n  {name}\n\n"
            "This will also remove all associated vehicles and service records.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.delete_customer(self._selected_customer_id):
                QMessageBox.information(self, "Deleted", "Customer deleted successfully.")
                self._reset_form()
                self.load_customers()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete customer.")
