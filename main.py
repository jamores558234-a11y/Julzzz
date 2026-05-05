"""Main application entry point - FIXED"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.login_window import LoginWindow
from views.dashboard_window import DashboardWindow


class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.dashboard_window = None
        self.show_login()

    def show_login(self):
        """Show login window"""
        try:
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self.show_dashboard)
            self.login_window.show()
        except Exception as e:
            print(f"Error showing login: {e}")

    def show_dashboard(self, user):
        """Show dashboard window"""
        try:
            self.dashboard_window = DashboardWindow(user)
            self.dashboard_window.logout_signal.connect(self.on_logout)
            self.dashboard_window.show()
            if self.login_window:
                self.login_window.close()
        except Exception as e:
            print(f"Error showing dashboard: {e}")

    def on_logout(self):
        """Handle logout"""
        try:
            if self.dashboard_window:
                self.dashboard_window.close()
            self.show_login()
        except Exception as e:
            print(f"Error on logout: {e}")

    def run(self):
        """Run application"""
        try:
            sys.exit(self.app.exec())
        except Exception as e:
            print(f"Error running app: {e}")


if __name__ == "__main__":
    try:
        manager = ApplicationManager()
        manager.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)