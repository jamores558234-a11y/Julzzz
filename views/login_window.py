from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QComboBox, QMessageBox, QFrame, QSizePolicy,
                             QGraphicsDropShadowEffect)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.auth_controller import AuthController


class LoginWindow(QWidget):
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.auth_controller = AuthController()
        self.init_ui()

    def init_ui(self):
        """Initialize login UI with formal design"""
        self.setWindowTitle("Julz Car AC Service - Login")
        self.setMinimumSize(560, 680)
        self.resize(1280, 800)

        self.setStyleSheet("""
            QWidget#outerWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a,
                    stop:0.5 #1e3a5f,
                    stop:1 #0f172a
                );
            }
        """)
        self.setObjectName("outerWidget")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Top brand strip ────────────────────────────────────────────────
        top_strip = QWidget()
        top_strip.setFixedHeight(68)
        top_strip.setStyleSheet("background: transparent;")
        ts_layout = QHBoxLayout(top_strip)
        ts_layout.setContentsMargins(48, 0, 48, 0)

        brand = QLabel("⚙  Julz Car AC Service")
        brand.setStyleSheet("color:#ffffff;font-size:15px;font-weight:700;letter-spacing:0.5px;font-family:'Segoe UI',sans-serif;")
        ts_layout.addWidget(brand, alignment=Qt.AlignmentFlag.AlignVCenter)
        ts_layout.addStretch()

        copy_lbl = QLabel("© 2025  All Rights Reserved")
        copy_lbl.setStyleSheet("color:rgba(255,255,255,0.35);font-size:11px;font-family:'Segoe UI',sans-serif;")
        ts_layout.addWidget(copy_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)

        root_layout.addWidget(top_strip)

        # ── Center row: tagline LEFT + card RIGHT ──────────────────────────
        center = QHBoxLayout()
        center.setContentsMargins(64, 0, 64, 0)
        center.setSpacing(64)

        # Left tagline panel
        left = QWidget()
        left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        left.setStyleSheet("background:transparent;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addStretch()

        h1 = QLabel("Management\nSystem")
        h1.setStyleSheet("color:#ffffff;font-size:48px;font-weight:800;font-family:'Segoe UI',sans-serif;line-height:1.1;")
        left_layout.addWidget(h1)

        sub = QLabel("Your all-in-one platform for car\nair-conditioning service management.")
        sub.setStyleSheet("color:rgba(255,255,255,0.5);font-size:14px;font-family:'Segoe UI',sans-serif;margin-top:16px;")
        left_layout.addWidget(sub)

        accent_bar = QFrame()
        accent_bar.setFixedSize(52, 5)
        accent_bar.setStyleSheet("background:#3b82f6;border-radius:3px;margin-top:22px;")
        left_layout.addWidget(accent_bar)

        left_layout.addStretch()
        center.addWidget(left)

        # ── Login Card ─────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(430)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        card.setStyleSheet("""
            QFrame#loginCard {
                background-color: #ffffff;
                border-radius: 18px;
            }
            QLabel {
                color: #1f2937;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit, QComboBox {
                padding: 11px 14px;
                border: 1.5px solid #d1d5db;
                border-radius: 8px;
                font-size: 13px;
                background-color: #f9fafb;
                color: #111827;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1.5px solid #2563eb;
                background-color: #ffffff;
            }
            QComboBox::drop-down { border: none; width: 28px; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1f2937;
                selection-background-color: #eff6ff;
                selection-color: #1d4ed8;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#signInBtn {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: white;
                padding: 13px;
                border: none;
                border-radius: 9px;
                font-weight: 700;
                font-size: 14px;
                letter-spacing: 0.5px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#signInBtn:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1d4ed8, stop:1 #1e40af);
            }
            QPushButton#signInBtn:pressed {
                background: #1e3a8a;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(52)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(0, 0, 0, 90))
        card.setGraphicsEffect(shadow)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(42, 42, 42, 42)
        cl.setSpacing(0)

        hd = QLabel("Sign In")
        hd.setStyleSheet("font-size:26px;font-weight:800;color:#111827;font-family:'Segoe UI',sans-serif;")
        cl.addWidget(hd)

        hd_sub = QLabel("Enter your credentials to access the system")
        hd_sub.setStyleSheet("font-size:12px;color:#6b7280;font-family:'Segoe UI',sans-serif;margin-top:4px;")
        cl.addWidget(hd_sub)
        cl.addSpacing(30)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size:12px;font-weight:600;color:#374151;font-family:'Segoe UI',sans-serif;margin-bottom:6px;")
            return lbl

        cl.addWidget(field_label("Username"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(44)
        cl.addWidget(self.username_input)
        cl.addSpacing(18)

        cl.addWidget(field_label("Password"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(44)
        cl.addWidget(self.password_input)
        cl.addSpacing(18)

        cl.addWidget(field_label("User Role"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(['Admin', 'Staff', 'Mechanic'])
        self.role_combo.setMinimumHeight(44)
        cl.addWidget(self.role_combo)
        cl.addSpacing(30)

        login_btn = QPushButton("Sign In  →")
        login_btn.setObjectName("signInBtn")
        login_btn.setMinimumHeight(50)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        cl.addWidget(login_btn)
        cl.addSpacing(26)

        # Demo box
        demo_frame = QFrame()
        demo_frame.setStyleSheet("""
            QFrame {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 10px;
            }
        """)
        dl = QVBoxLayout(demo_frame)
        dl.setContentsMargins(16, 12, 16, 12)
        dl.setSpacing(5)

        demo_t = QLabel("🔑  Demo Credentials")
        demo_t.setStyleSheet("color:#1e40af;font-weight:700;font-size:12px;font-family:'Segoe UI',sans-serif;")
        dl.addWidget(demo_t)

        demo_v = QLabel("Username: admin   ·   Password: admin123   ·   Role: Admin")
        demo_v.setStyleSheet("color:#1d4ed8;font-size:11px;font-family:'Consolas','Courier New',monospace;")
        demo_v.setWordWrap(True)
        dl.addWidget(demo_v)

        cl.addWidget(demo_frame)
        cl.addStretch()

        center.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)
        root_layout.addLayout(center, stretch=1)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(38)
        footer.setStyleSheet("background:transparent;")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 0, 0, 0)
        ft = QLabel("Julz Car AC Service  ·  Secure Login Portal")
        ft.setStyleSheet("color:rgba(255,255,255,0.2);font-size:11px;font-family:'Segoe UI',sans-serif;")
        fl.addWidget(ft, alignment=Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(footer)

    def handle_login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation Error", "Please enter username and password")
            return

        user = self.auth_controller.authenticate_user(username, password)

        if user:
            self.login_success.emit(user)
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "Authentication Error", "Invalid username or password")

    def clear_inputs(self):
        """Clear input fields"""
        self.username_input.clear()
        self.password_input.clear()
