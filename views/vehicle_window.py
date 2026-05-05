"""Vehicle management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QFrame, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.vehicle_controller import VehicleController
from controllers.customer_controller import CustomerController
from utils.validators import validate_not_empty
from views.widgets import (SHARED_INPUT_STYLE, SHARED_TABLE_STYLE,
                           btn_style, section_label, SearchableComboBox)


class VehicleWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.vehicle_controller = VehicleController()
        self.customer_controller = CustomerController()
        self._selected_vehicle_id = None
        self.init_ui()
        self.refresh_all()

    # ── Called every time this tab becomes visible ─────────────────────────────
    def showEvent(self, event):
        """Reload customers into combo every time this window is shown"""
        super().showEvent(event)
        self._reload_customer_combo()

    def refresh_all(self):
        self._reload_customer_combo()
        self.load_vehicles()

    def _reload_customer_combo(self):
        """Always fetch fresh customer list from DB"""
        try:
            customers = self.customer_controller.get_all_customers()
            items = []
            for c in customers:
                mid = (' ' + c['middle_name']) if c.get('middle_name') else ''
                label = f"{c['last_name']}, {c['first_name']}{mid}"
                items.append((label, c['customer_id']))
            self.customer_combo.populate(items)
        except Exception as e:
            print(f"Error loading customers into combo: {e}")

    # ── UI Setup ───────────────────────────────────────────────────────────────

    def init_ui(self):
        self.setStyleSheet("background-color:#f8fafc;font-family:'Segoe UI',sans-serif;")
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
        frame.setStyleSheet("QFrame{background:#ffffff;border-bottom:2px solid #e2e8f0;border-radius:0;}")
        h = QVBoxLayout(frame)
        h.setContentsMargins(16, 8, 16, 8)
        t = QLabel("🚗  Vehicle Management")
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        h.addWidget(t)
        sub = QLabel("Add, search, update, and delete vehicle records")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        h.addWidget(sub)
        return frame

    def _build_search_bar(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;}")
        row = QHBoxLayout(frame)
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(10)

        lbl = QLabel("🔍")
        lbl.setStyleSheet("font-size:16px;")
        row.addWidget(lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by plate, model, customer name…")
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
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;}")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(8)

        hdr = QLabel("Vehicle Details")
        hdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(hdr)

        # Customer searchable combo
        fl.addWidget(section_label("Customer *  (type to search)"))
        self.customer_combo = SearchableComboBox()
        fl.addWidget(self.customer_combo)

        # Row 1: Plate | Model | Type
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        pl_col = QVBoxLayout()
        pl_col.addWidget(section_label("Plate Number *"))
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("ABC-1234")
        self.plate_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.plate_input.setMinimumHeight(36)
        pl_col.addWidget(self.plate_input)
        row1.addLayout(pl_col)

        mo_col = QVBoxLayout()
        mo_col.addWidget(section_label("Model *"))
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Toyota Camry")
        self.model_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.model_input.setMinimumHeight(36)
        mo_col.addWidget(self.model_input)
        row1.addLayout(mo_col)

        ty_col = QVBoxLayout()
        ty_col.addWidget(section_label("Type *"))
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Sedan / SUV / Van")
        self.type_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.type_input.setMinimumHeight(36)
        ty_col.addWidget(self.type_input)
        row1.addLayout(ty_col)

        fl.addLayout(row1)

        # Row 2: Year | Color
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        yr_col = QVBoxLayout()
        yr_col.addWidget(section_label("Year"))
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("2020")
        self.year_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.year_input.setMinimumHeight(36)
        yr_col.addWidget(self.year_input)
        row2.addLayout(yr_col)

        cl_col = QVBoxLayout()
        cl_col.addWidget(section_label("Color"))
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Silver")
        self.color_input.setStyleSheet(SHARED_INPUT_STYLE)
        self.color_input.setMinimumHeight(36)
        cl_col.addWidget(self.color_input)
        row2.addLayout(cl_col)

        row2.addStretch()
        fl.addLayout(row2)

        return frame

    def _build_buttons(self):
        row = QHBoxLayout()
        row.setSpacing(10)

        self.add_btn = QPushButton("➕  Add Vehicle")
        self.add_btn.setStyleSheet(btn_style("#10b981", "#059669", "#047857"))
        self.add_btn.setMinimumHeight(38)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_vehicle)
        row.addWidget(self.add_btn)

        self.update_btn = QPushButton("✏️  Update")
        self.update_btn.setStyleSheet(btn_style("#3b82f6", "#2563eb", "#1d4ed8"))
        self.update_btn.setMinimumHeight(38)
        self.update_btn.setEnabled(False)
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.clicked.connect(self.update_vehicle)
        row.addWidget(self.update_btn)

        self.delete_btn = QPushButton("🗑️  Delete")
        self.delete_btn.setStyleSheet(btn_style("#ef4444", "#dc2626", "#b91c1c"))
        self.delete_btn.setMinimumHeight(38)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self.delete_vehicle)
        row.addWidget(self.delete_btn)

        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setStyleSheet(btn_style("#8b5cf6", "#7c3aed"))
        refresh_btn.setMinimumHeight(38)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_all)
        row.addWidget(refresh_btn)

        clear_btn = QPushButton("✖  Clear Form")
        clear_btn.setStyleSheet(btn_style("#6b7280", "#4b5563"))
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._reset_form)
        row.addWidget(clear_btn)

        row.addStretch()

        self.selection_lbl = QLabel("No record selected")
        self.selection_lbl.setStyleSheet("""
            color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;
            background:#f3f4f6;border-radius:6px;padding:6px 12px;
        """)
        row.addWidget(self.selection_lbl)

        return row

    def _build_table(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(frame)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ['ID', 'Customer', 'Plate', 'Model', 'Type', 'Year', 'Color', 'CustID'])
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(7, True)
        self.table.clicked.connect(self.on_row_clicked)
        self.table.setStyleSheet(
            SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)

        return frame

    # ── Data ──────────────────────────────────────────────────────────────────

    def load_vehicles(self):
        try:
            vehicles = self.vehicle_controller.get_all_vehicles() or []
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load vehicles: {e}")
            return

        self.table.setRowCount(len(vehicles))
        for row, v in enumerate(vehicles):
            self.table.setItem(row, 0, QTableWidgetItem(str(v.get('vehicle_id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(v.get('customer_name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(v.get('plate_number', '')))
            self.table.setItem(row, 3, QTableWidgetItem(v.get('model', '')))
            self.table.setItem(row, 4, QTableWidgetItem(v.get('type', '')))
            self.table.setItem(row, 5, QTableWidgetItem(str(v.get('year', ''))))
            self.table.setItem(row, 6, QTableWidgetItem(v.get('color', '')))
            self.table.setItem(row, 7, QTableWidgetItem(str(v.get('customer_id', ''))))

    def _on_search(self, text):
        kw = text.lower().strip()
        for row in range(self.table.rowCount()):
            match = any(
                kw in (self.table.item(row, col).text().lower()
                       if self.table.item(row, col) else '')
                for col in range(1, 7)
            )
            self.table.setRowHidden(row, not match if kw else False)
        self._reset_selection()

    def _clear_search(self):
        self.search_input.clear()
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, False)
        self._reset_selection()

    # ── Row click ─────────────────────────────────────────────────────────────

    def on_row_clicked(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self._selected_vehicle_id = int(self.table.item(row, 0).text())
        customer_id = int(self.table.item(row, 7).text())

        self.customer_combo.set_selection_by_id(customer_id)
        self.plate_input.setText(self.table.item(row, 2).text())
        self.model_input.setText(self.table.item(row, 3).text())
        self.type_input.setText(self.table.item(row, 4).text())
        self.year_input.setText(self.table.item(row, 5).text())
        self.color_input.setText(self.table.item(row, 6).text())

        self.delete_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        plate = self.table.item(row, 2).text()
        model = self.table.item(row, 3).text()
        self.selection_lbl.setText(f"Selected: {plate} — {model}")
        self.selection_lbl.setStyleSheet("""
            color:#1d4ed8;font-size:12px;font-family:'Segoe UI',sans-serif;
            background:#dbeafe;border-radius:6px;padding:6px 12px;font-weight:600;
        """)

    def _reset_selection(self):
        self._selected_vehicle_id = None
        self.delete_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.selection_lbl.setText("No record selected")
        self.selection_lbl.setStyleSheet("""
            color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;
            background:#f3f4f6;border-radius:6px;padding:6px 12px;
        """)

    def _reset_form(self):
        self.customer_combo.clear_selection()
        self.plate_input.clear()
        self.model_input.clear()
        self.type_input.clear()
        self.year_input.clear()
        self.color_input.clear()
        self._reset_selection()
        self.table.clearSelection()

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def add_vehicle(self):
        try:
            customer_id = self.customer_combo.current_data()
            if not customer_id:
                QMessageBox.warning(self, "Validation Error",
                    "Please select a valid customer from the dropdown.")
                return
            plate = self.plate_input.text().strip()
            model = self.model_input.text().strip()
            type_val = self.type_input.text().strip()
            year = self.year_input.text().strip()
            color = self.color_input.text().strip()

            if not validate_not_empty(plate, model, type_val):
                QMessageBox.warning(self, "Validation Error",
                    "Plate number, model, and type are required.")
                return
            try:
                year = int(year) if year else None
            except ValueError:
                QMessageBox.warning(self, "Error", "Year must be a number.")
                return

            if self.vehicle_controller.add_vehicle(
                    customer_id, plate, model, type_val, year, color):
                QMessageBox.information(self, "Success", "Vehicle added successfully.")
                self._reset_form()
                self.load_vehicles()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to add vehicle.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_vehicle(self):
        if not self._selected_vehicle_id:
            QMessageBox.warning(self, "Selection Error",
                "Please select a vehicle from the table first.")
            return
        try:
            customer_id = self.customer_combo.current_data()
            if not customer_id:
                QMessageBox.warning(self, "Validation Error",
                    "Please select a valid customer from the dropdown.")
                return
            plate = self.plate_input.text().strip()
            model = self.model_input.text().strip()
            type_val = self.type_input.text().strip()
            year = self.year_input.text().strip()
            color = self.color_input.text().strip()

            if not validate_not_empty(plate, model, type_val):
                QMessageBox.warning(self, "Validation Error",
                    "Plate number, model, and type are required.")
                return
            try:
                year = int(year) if year else None
            except ValueError:
                QMessageBox.warning(self, "Error", "Year must be a number.")
                return

            if self.vehicle_controller.update_vehicle(
                    self._selected_vehicle_id, customer_id, plate, model, type_val, year, color):
                QMessageBox.information(self, "Success", "Vehicle updated successfully.")
                self._reset_form()
                self.load_vehicles()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to update vehicle.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_vehicle(self):
        if not self._selected_vehicle_id:
            QMessageBox.warning(self, "Selection Error",
                "You must select a vehicle from the table before deleting.")
            return

        row = self.table.currentRow()
        plate = self.table.item(row, 2).text()
        model = self.table.item(row, 3).text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete:\n\n"
            f"  {plate} — {model}\n\n"
            "This will also remove all associated service records.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.vehicle_controller.delete_vehicle(self._selected_vehicle_id):
                QMessageBox.information(self, "Deleted", "Vehicle deleted successfully.")
                self._reset_form()
                self.load_vehicles()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete vehicle.")
