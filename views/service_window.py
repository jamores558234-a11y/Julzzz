"""Service management window"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
                             QTextEdit, QFrame, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.service_controller import ServiceController
from controllers.vehicle_controller import VehicleController
from database.connection import DatabaseConnection
from views.widgets import SHARED_INPUT_STYLE, SHARED_TABLE_STYLE, btn_style, section_label


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

        # Header
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

        # Form (only for non-mechanics)
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

            vc = QVBoxLayout()
            vc.addWidget(section_label("Vehicle *"))
            self.vehicle_combo = QComboBox()
            self.vehicle_combo.setStyleSheet(SHARED_INPUT_STYLE.replace("QLineEdit","QComboBox"))
            self.vehicle_combo.setMinimumHeight(42)
            try: self.load_vehicles_combo()
            except: pass
            vc.addWidget(self.vehicle_combo)
            row1.addLayout(vc)

            mc = QVBoxLayout()
            mc.addWidget(section_label("Mechanic"))
            self.mechanic_combo = QComboBox()
            self.mechanic_combo.setStyleSheet(SHARED_INPUT_STYLE.replace("QLineEdit","QComboBox"))
            self.mechanic_combo.setMinimumHeight(42)
            try: self.load_mechanics_combo()
            except: pass
            mc.addWidget(self.mechanic_combo)
            row1.addLayout(mc)

            sc = QVBoxLayout()
            sc.addWidget(section_label("Status"))
            self.status_combo = QComboBox()
            self.status_combo.addItems(['Pending','Ongoing','Completed'])
            self.status_combo.setStyleSheet(SHARED_INPUT_STYLE.replace("QLineEdit","QComboBox"))
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
                    background:#f9fafb;
                    color:#111827;
                    font-family:'Segoe UI',sans-serif;
                }
                QTextEdit:focus { border:1.5px solid #2563eb; background:#fff; }
            """)
            fl.addWidget(self.issue_input)
            layout.addWidget(ff)

        # Buttons
        br = QHBoxLayout()
        br.setSpacing(10)

        if self.user_role != 'Mechanic':
            cb = QPushButton("➕  Create Service")
            cb.setStyleSheet(btn_style("#10b981","#059669","#047857"))
            cb.setMinimumHeight(44)
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.clicked.connect(self.create_service)
            br.addWidget(cb)

        ub = QPushButton("✏️  Update Status")
        ub.setStyleSheet(btn_style("#3b82f6","#2563eb","#1d4ed8"))
        ub.setMinimumHeight(44)
        ub.setCursor(Qt.CursorShape.PointingHandCursor)
        ub.clicked.connect(self.update_status)
        br.addWidget(ub)

        rb = QPushButton("🔄  Refresh")
        rb.setStyleSheet(btn_style("#8b5cf6","#7c3aed"))
        rb.setMinimumHeight(44)
        rb.setCursor(Qt.CursorShape.PointingHandCursor)
        rb.clicked.connect(self.load_services)
        br.addWidget(rb)

        br.addStretch()

        self.selection_lbl = QLabel("No record selected")
        self.selection_lbl.setStyleSheet("color:#6b7280;font-size:12px;background:#f3f4f6;border-radius:6px;padding:6px 12px;font-family:'Segoe UI',sans-serif;")
        br.addWidget(self.selection_lbl)

        layout.addLayout(br)

        # Table
        tf = QFrame()
        tf.setStyleSheet("QFrame{background:#fff;border:1px solid #e5e7eb;border-radius:10px;}")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID','Vehicle','Customer','Mechanic','Issue','Status','Created','VehicleID'])
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

    def load_vehicles_combo(self):
        vehicles = self.vehicle_controller.get_all_vehicles()
        if vehicles:
            for v in vehicles:
                self.vehicle_combo.addItem(f"{v.get('plate_number','')} — {v.get('model','')}", v.get('vehicle_id'))

    def load_mechanics_combo(self):
        mechanics = self.db.execute_query("SELECT user_id, full_name FROM users WHERE role = 'Mechanic'")
        if mechanics:
            for m in mechanics:
                self.mechanic_combo.addItem(m.get('full_name',''), m.get('user_id'))

    def load_services(self):
        try:
            if self.user_role == 'Mechanic':
                query = """
                SELECT s.*, v.plate_number, v.model,
                CONCAT(c.first_name,' ',IFNULL(c.middle_name,''),' ',c.last_name) as customer_name,
                u.full_name as mechanic_name
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

            status_colors = {"Pending":"#fef3c7","Ongoing":"#dbeafe","Completed":"#d1fae5"}

            for row, s in enumerate(services):
                self.table.setItem(row,0,QTableWidgetItem(str(s.get('service_id',''))))
                self.table.setItem(row,1,QTableWidgetItem(f"{s.get('plate_number','')} — {s.get('model','')}"))
                self.table.setItem(row,2,QTableWidgetItem(s.get('customer_name','')))
                self.table.setItem(row,3,QTableWidgetItem(s.get('mechanic_name','Unassigned')))
                self.table.setItem(row,4,QTableWidgetItem((s.get('issue_complaint','') or '')[:60]))
                status = s.get('status','')
                si = QTableWidgetItem(status)
                self.table.setItem(row,5,si)
                self.table.setItem(row,6,QTableWidgetItem(str(s.get('created_at',''))[:16]))
                self.table.setItem(row,7,QTableWidgetItem(str(s.get('vehicle_id',''))))
        except Exception as e:
            print(f"Error loading services: {e}")

    def on_row_clicked(self):
        row = self.table.currentRow()
        if row < 0: return
        self._selected_service_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 5).text()
        vehicle_plate = self.table.item(row, 1).text()
        if self.user_role != 'Mechanic':
            vid = int(self.table.item(row, 7).text())
            self.vehicle_combo.setCurrentIndex(self.vehicle_combo.findData(vid))
            self.status_combo.setCurrentText(status)
        self.selection_lbl.setText(f"Selected: {vehicle_plate}  ·  {status}")
        self.selection_lbl.setStyleSheet("color:#1d4ed8;font-size:12px;background:#dbeafe;border-radius:6px;padding:6px 12px;font-weight:600;font-family:'Segoe UI',sans-serif;")

    def create_service(self):
        try:
            vehicle_id = self.vehicle_combo.currentData()
            if not vehicle_id:
                QMessageBox.warning(self,"Validation Error","Please select a vehicle.")
                return
            mechanic_id = self.mechanic_combo.currentData()
            issue = self.issue_input.toPlainText().strip()
            if not issue:
                QMessageBox.warning(self,"Validation Error","Please enter the issue or complaint.")
                return
            if self.service_controller.create_service(vehicle_id, mechanic_id, issue):
                QMessageBox.information(self,"Success","Service created successfully.")
                self.issue_input.clear()
                self.load_services()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self,"Error","Failed to create service.")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))

    def update_status(self):
        try:
            row = self.table.currentRow()
            if row < 0:
                QMessageBox.warning(self,"Selection Error","Please select a service from the table first.")
                return
            service_id = int(self.table.item(row, 0).text())
            if self.user_role == 'Mechanic':
                current = self.table.item(row, 5).text()
                new_status = {'Pending':'Ongoing','Ongoing':'Completed'}.get(current)
                if not new_status:
                    QMessageBox.warning(self,"Error","Service is already completed.")
                    return
            else:
                new_status = self.status_combo.currentText()
            if self.service_controller.update_service_status(service_id, new_status):
                QMessageBox.information(self,"Success","Status updated successfully.")
                self.load_services()
                self.data_changed.emit()
            else:
                QMessageBox.warning(self,"Error","Failed to update status.")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))