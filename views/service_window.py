"""Service management window - with searchable & auto-refreshing vehicle dropdown"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
                             QTextEdit, QFrame, QHeaderView, QLineEdit, QListWidget,
                             QListWidgetItem, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from controllers.service_controller import ServiceController
from controllers.vehicle_controller import VehicleController
from database.connection import DatabaseConnection
from views.widgets import SHARED_INPUT_STYLE, SHARED_TABLE_STYLE, btn_style, section_label


# ──────────────────────────────────────────────────────────────
#  Searchable Vehicle ComboBox Widget
# ──────────────────────────────────────────────────────────────
class SearchableVehicleCombo(QWidget):
    """Type plate number or model → dropdown filters instantly."""

    vehicle_selected = pyqtSignal(int, str)  # emits (vehicle_id, display_text)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vehicles = []       # list of (vehicle_id, display_text)
        self._selected_id = None
        self._selected_text = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type plate number or model to search...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1.5px solid #d1d5db;
                border-radius: 8px;
                font-size: 13px;
                background: #f9fafb;
                color: #111827;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border: 1.5px solid #2563eb;
                background: #fff;
            }
        """)
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.focusOutEvent = self._on_focus_out
        layout.addWidget(self.search_input)

        # Dropdown list (hidden by default)
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(200)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1.5px solid #2563eb;
                border-top: none;
                border-radius: 0 0 8px 8px;
                background: #fff;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                color: #111827;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #f3f4f6;
            }
            QListWidget::item:hover {
                background: #eff6ff;
                color: #1d4ed8;
            }
            QListWidget::item:selected {
                background: #2563eb;
                color: #fff;
            }
        """)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.hide()
        layout.addWidget(self.list_widget)

    def load_vehicles(self, vehicles):
        """Load vehicles: list of dicts with vehicle_id, plate_number, model"""
        self._vehicles = [
            (v.get('vehicle_id'), f"{v.get('plate_number', '')} — {v.get('model', '')}")
            for v in (vehicles or [])
        ]
        self._refresh_list(self.search_input.text())

    def _on_text_changed(self, text):
        self._selected_id = None  # clear selection when typing
        self._refresh_list(text)

        # Auto-select if text exactly matches a vehicle
        for vid, display in self._vehicles:
            if text.strip().lower() == display.lower():
                self._selected_id = vid
                self._selected_text = display
                self.list_widget.hide()
                return

        if text.strip():
            self.list_widget.show()
        else:
            self.list_widget.hide()

    def _refresh_list(self, text):
        self.list_widget.clear()
        keyword = text.strip().lower()
        for vid, display in self._vehicles:
            if keyword in display.lower():
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, vid)
                self.list_widget.addItem(item)

    def _on_item_clicked(self, item):
        self._selected_id = item.data(Qt.ItemDataRole.UserRole)
        self._selected_text = item.text()
        self.search_input.setText(self._selected_text)
        self.list_widget.hide()
        self.vehicle_selected.emit(self._selected_id, self._selected_text)

    def _on_focus_out(self, event):
        # Small delay so list click registers first
        QTimer.singleShot(150, self.list_widget.hide)
        QLineEdit.focusOutEvent(self.search_input, event)

    def currentData(self):
        """Returns selected vehicle_id or None"""
        return self._selected_id

    def currentText(self):
        """Returns selected display text"""
        return self._selected_text

    def setCurrentByVehicleId(self, vehicle_id):
        """Set selection by vehicle_id (used when clicking table row)"""
        for vid, display in self._vehicles:
            if vid == vehicle_id:
                self._selected_id = vid
                self._selected_text = display
                self.search_input.setText(display)
                self.list_widget.hide()
                return

    def clear_selection(self):
        """Reset the combo"""
        self._selected_id = None
        self._selected_text = ""
        self.search_input.clear()
        self.list_widget.hide()


# ──────────────────────────────────────────────────────────────
#  Service Window
# ──────────────────────────────────────────────────────────────
class ServiceWindow(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, user=None):
        super().__init__()
        self.user = user or {}
        self.user_role = self.user.get('role', 'Staff')
        self.user_id = self.user.get('user_id')
        self.service_controller = ServiceController()
        self.vehicle_controller = VehicleController()
        self.db = DatabaseConnection()
        self._selected_service_id = None
        self.init_ui()
        try:
            self.load_services()
        except Exception as e:
            print(f"Error loading services: {e}")

    def init_ui(self):
        self.setStyleSheet("background:#f8fafc;font-family:'Segoe UI',sans-serif;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Header ──────────────────────────────────────────────
        hf = QFrame()
        hf.setStyleSheet("QFrame{background:#fff;border-bottom:2px solid #e2e8f0;}")
        hl = QVBoxLayout(hf)
        hl.setContentsMargins(16, 12, 16, 12)
        title_text = "🔧  My Services" if self.user_role == 'Mechanic' else "🔧  Service Management"
        t = QLabel(title_text)
        t.setStyleSheet("color:#1f2937;font-size:24px;font-weight:700;font-family:'Segoe UI',sans-serif;")
        hl.addWidget(t)
        sub = QLabel("Create and manage vehicle service records")
        sub.setStyleSheet("color:#6b7280;font-size:12px;font-family:'Segoe UI',sans-serif;margin-top:2px;")
        hl.addWidget(sub)
        layout.addWidget(hf)

        # ── Form (Admin / Staff only) ────────────────────────────
        if self.user_role != 'Mechanic':
            ff = QFrame()
            ff.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
            fl = QVBoxLayout(ff)
            fl.setContentsMargins(20, 16, 20, 16)
            fl.setSpacing(14)

            fhdr = QLabel("Service Details")
            fhdr.setStyleSheet("color:#1f2937;font-size:14px;font-weight:700;font-family:'Segoe UI',sans-serif;")
            fl.addWidget(fhdr)

            row1 = QHBoxLayout()
            row1.setSpacing(14)

            # ── Searchable Vehicle Combo ──
            vc = QVBoxLayout()
            vc.addWidget(section_label("Vehicle *"))
            self.vehicle_combo = SearchableVehicleCombo()
            self.vehicle_combo.setMinimumHeight(42)
            vc.addWidget(self.vehicle_combo)
            row1.addLayout(vc)

            # ── Mechanic Combo ──
            mc = QVBoxLayout()
            mc.addWidget(section_label("Mechanic"))
            self.mechanic_combo = QComboBox()
            self.mechanic_combo.setStyleSheet(SHARED_INPUT_STYLE.replace("QLineEdit", "QComboBox"))
            self.mechanic_combo.setMinimumHeight(42)
            try:
                self.load_mechanics_combo()
            except Exception as e:
                print(f"Error loading mechanics: {e}")
            mc.addWidget(self.mechanic_combo)
            row1.addLayout(mc)

            # ── Status Combo ──
            sc = QVBoxLayout()
            sc.addWidget(section_label("Status"))
            self.status_combo = QComboBox()
            self.status_combo.addItems(['Pending', 'Ongoing', 'Completed'])
            self.status_combo.setStyleSheet(SHARED_INPUT_STYLE.replace("QLineEdit", "QComboBox"))
            self.status_combo.setMinimumHeight(42)
            sc.addWidget(self.status_combo)
            row1.addLayout(sc)

            fl.addLayout(row1)

            fl.addWidget(section_label("Issue / Complaint *"))
            self.issue_input = QTextEdit()
            self.issue_input.setMaximumHeight(80)
            self.issue_input.setStyleSheet("""
                QTextEdit {
                    padding: 10px 14px;
                    border: 1.5px solid #d1d5db;
                    border-radius: 8px;
                    font-size: 13px;
                    background: #f9fafb;
                    color: #111827;
                    font-family: 'Segoe UI', sans-serif;
                }
                QTextEdit:focus { border: 1.5px solid #2563eb; background: #fff; }
            """)
            fl.addWidget(self.issue_input)
            layout.addWidget(ff)

        # ── Buttons ──────────────────────────────────────────────
        br = QHBoxLayout()
        br.setSpacing(10)

        if self.user_role != 'Mechanic':
            cb = QPushButton("➕  Create Service")
            cb.setStyleSheet(btn_style("#10b981", "#059669", "#047857"))
            cb.setMinimumHeight(44)
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.clicked.connect(self.create_service)
            br.addWidget(cb)

        ub = QPushButton("✏️  Update Status")
        ub.setStyleSheet(btn_style("#3b82f6", "#2563eb", "#1d4ed8"))
        ub.setMinimumHeight(44)
        ub.setCursor(Qt.CursorShape.PointingHandCursor)
        ub.clicked.connect(self.update_status)
        br.addWidget(ub)

        rb = QPushButton("🔄  Refresh")
        rb.setStyleSheet(btn_style("#8b5cf6", "#7c3aed"))
        rb.setMinimumHeight(44)
        rb.setCursor(Qt.CursorShape.PointingHandCursor)
        rb.clicked.connect(self.refresh_all)
        br.addWidget(rb)

        br.addStretch()

        self.selection_lbl = QLabel("No record selected")
        self.selection_lbl.setStyleSheet(
            "color:#6b7280;font-size:12px;background:#f3f4f6;"
            "border-radius:6px;padding:6px 12px;font-family:'Segoe UI',sans-serif;"
        )
        br.addWidget(self.selection_lbl)
        layout.addLayout(br)

        # ── Table ────────────────────────────────────────────────
        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ['ID', 'Vehicle', 'Customer', 'Mechanic', 'Issue', 'Status', 'Created', 'VehicleID'])
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(7, True)
        self.table.clicked.connect(self.on_row_clicked)
        self.table.setStyleSheet(SHARED_TABLE_STYLE + "QTableWidget{alternate-background-color:#fafafa;}")
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        tl.addWidget(self.table)
        layout.addWidget(tf)

    # ── Data Loaders ─────────────────────────────────────────────

    def load_vehicles_combo(self):
        """Always reload fresh from DB"""
        try:
            vehicles = self.vehicle_controller.get_all_vehicles()
            self.vehicle_combo.clear_selection()
            self.vehicle_combo.load_vehicles(vehicles or [])
        except Exception as e:
            print(f"Error loading vehicles: {e}")

    def load_mechanics_combo(self):
        mechanics = self.db.execute_query(
            "SELECT user_id, full_name FROM users WHERE role = 'Mechanic'")
        if mechanics:
            for m in mechanics:
                self.mechanic_combo.addItem(m.get('full_name', ''), m.get('user_id'))

    def load_services(self):
        try:
            if self.user_role == 'Mechanic':
                query = """
                    SELECT s.*, v.plate_number, v.model,
                    CONCAT(c.first_name,' ',IFNULL(c.middle_name,''),' ',c.last_name) AS customer_name,
                    u.full_name AS mechanic_name
                    FROM services s
                    JOIN vehicles v ON s.vehicle_id = v.vehicle_id
                    JOIN customers c ON v.customer_id = c.customer_id
                    LEFT JOIN users u ON s.mechanic_id = u.user_id
                    WHERE s.mechanic_id = %s ORDER BY s.created_at DESC
                """
                services = self.db.execute_query(query, (self.user_id,))
            else:
                services = self.service_controller.get_all_services()

            services = services or []
            self.table.setRowCount(len(services))

            for row, s in enumerate(services):
                self.table.setItem(row, 0, QTableWidgetItem(str(s.get('service_id', ''))))
                self.table.setItem(row, 1, QTableWidgetItem(
                    f"{s.get('plate_number', '')} — {s.get('model', '')}"))
                self.table.setItem(row, 2, QTableWidgetItem(s.get('customer_name', '')))
                self.table.setItem(row, 3, QTableWidgetItem(s.get('mechanic_name', 'Unassigned')))
                self.table.setItem(row, 4, QTableWidgetItem(
                    (s.get('issue_complaint', '') or '')[:60]))
                self.table.setItem(row, 5, QTableWidgetItem(s.get('status', '')))
                self.table.setItem(row, 6, QTableWidgetItem(
                    str(s.get('created_at', ''))[:16]))
                self.table.setItem(row, 7, QTableWidgetItem(str(s.get('vehicle_id', ''))))
        except Exception as e:
            print(f"Error loading services: {e}")

    def refresh_all(self):
        """Refresh both vehicle dropdown and services table"""
        if self.user_role != 'Mechanic':
            self.load_vehicles_combo()
        self.load_services()

    def refresh_vehicles(self):
        """Public method — call this from vehicle window after adding a vehicle"""
        if self.user_role != 'Mechanic':
            self.load_vehicles_combo()

    # ── Auto-refresh when switching to this tab ──────────────────
    def showEvent(self, event):
        """Reload vehicles every time this window becomes visible"""
        super().showEvent(event)
        if self.user_role != 'Mechanic':
            try:
                self.load_vehicles_combo()
            except Exception as e:
                print(f"Error refreshing vehicles on show: {e}")

    # ── Table row click ──────────────────────────────────────────
    def on_row_clicked(self):
        row = self.table.currentRow()
        if row < 0:
            return
        self._selected_service_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 5).text()
        vehicle_plate = self.table.item(row, 1).text()

        if self.user_role != 'Mechanic':
            vid = int(self.table.item(row, 7).text())
            self.vehicle_combo.setCurrentByVehicleId(vid)
            self.status_combo.setCurrentText(status)

        self.selection_lbl.setText(f"Selected: {vehicle_plate}  ·  {status}")
        self.selection_lbl.setStyleSheet(
            "color:#1d4ed8;font-size:12px;background:#dbeafe;border-radius:6px;"
            "padding:6px 12px;font-weight:600;font-family:'Segoe UI',sans-serif;"
        )

    # ── Actions ──────────────────────────────────────────────────
    def create_service(self):
        try:
            vehicle_id = self.vehicle_combo.currentData()
            if not vehicle_id:
                QMessageBox.warning(self, "Validation Error",
                                    "Please select a vehicle from the dropdown.")
                return
            mechanic_id = self.mechanic_combo.currentData()
            issue = self.issue_input.toPlainText().strip()
            if not issue:
                QMessageBox.warning(self, "Validation Error",
                                    "Please enter the issue or complaint.")
                return
            if self.service_controller.create_service(vehicle_id, mechanic_id, issue):
                QMessageBox.information(self, "Success", "Service created successfully.")
                self.issue_input.clear()
                self.vehicle_combo.clear_selection()
                self.load_services()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to create service.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_status(self):
        try:
            row = self.table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "Selection Error",
                                    "Please select a service from the table first.")
                return
            service_id = int(self.table.item(row, 0).text())
            if self.user_role == 'Mechanic':
                current = self.table.item(row, 5).text()
                new_status = {'Pending': 'Ongoing', 'Ongoing': 'Completed'}.get(current)
                if not new_status:
                    QMessageBox.warning(self, "Error", "Service is already completed.")
                    return
            else:
                new_status = self.status_combo.currentText()

            if self.service_controller.update_service_status(service_id, new_status):
                QMessageBox.information(self, "Success", "Status updated successfully.")
                self.load_services()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to update status.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))