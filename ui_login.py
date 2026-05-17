# ui_login.py
# ============================================================
# Smart City Management System - Login Window
# Handles both Citizen and Employee login + Citizen Registration
# ============================================================

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import models


class LoginWindow(QWidget):
    """
    Main login window with two tabs:
      1. Login (for Citizen or Employee)
      2. Register (for new Citizens only)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart City Management System - Login")
        self.setFixedSize(460, 400)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # --- Header ---
        title = QLabel("🏙️ Smart City Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(title)

        subtitle = QLabel("City Services Portal")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        main_layout.addWidget(subtitle)

        # --- Tab Widget ---
        tabs = QTabWidget()
        tabs.addTab(self._build_login_tab(),    "Login")
        tabs.addTab(self._build_register_tab(), "Register (Citizen)")
        main_layout.addWidget(tabs)

    # ----------------------------------------------------------
    # LOGIN TAB
    # ----------------------------------------------------------
    def _build_login_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)

        self.login_email    = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_email.setPlaceholderText("your@email.com")
        self.login_password.setPlaceholderText("••••••••")

        form.addRow("Email:",    self.login_email)
        form.addRow("Password:", self.login_password)
        layout.addLayout(form)

        # Hint label
        hint = QLabel("ℹ️ Employees (Admin/Officer/Worker) and Citizens share this login.")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(hint)

        # Login button
        btn_login = QPushButton("Login")
        btn_login.setFixedHeight(36)
        btn_login.setStyleSheet("background-color: #2563EB; color: white; border-radius: 4px; font-weight: bold;")
        btn_login.clicked.connect(self._handle_login)
        layout.addWidget(btn_login)

        layout.addStretch()

        # Demo accounts info box
        info = QLabel(
            "Demo Accounts:\n"
            "Admin    → admin@city.gov / admin123\n"
            "Officer  → officer@city.gov / officer123\n"
            "Worker   → worker@city.gov / worker123\n"
            "Citizen  → citizen@gmail.com / citizen123"
        )
        info.setStyleSheet(
            "background-color: #F0F4FF; border: 1px solid #CBD5E1; "
            "border-radius: 4px; padding: 8px; font-size: 11px; color: #334155;"
        )
        layout.addWidget(info)

        return widget

    def _handle_login(self):
        email    = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter email and password.")
            return

        # Try employee login first, then citizen
        user = models.authenticate(email, password, 'employee')
        if not user:
            user = models.authenticate(email, password, 'citizen')

        if not user:
            QMessageBox.warning(self, "Login Failed", "Invalid email or password.")
            return

        # Open appropriate dashboard
        self._open_dashboard(user)

    def _open_dashboard(self, user):
        """Import and open the correct dashboard based on user role."""
        role = user.get('role')

        if role == 'Admin' or role == 'Officer':
            from ui_admin import AdminDashboard
            self.dashboard = AdminDashboard(user)

        elif role == 'Worker':
            from ui_worker import WorkerDashboard
            self.dashboard = WorkerDashboard(user)

        elif role == 'Citizen':
            from ui_citizen import CitizenDashboard
            self.dashboard = CitizenDashboard(user)

        else:
            QMessageBox.critical(self, "Error", f"Unknown role: {role}")
            return

        self.dashboard.show()
        self.close()

    # ----------------------------------------------------------
    # REGISTER TAB
    # ----------------------------------------------------------
    def _build_register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)

        self.reg_name     = QLineEdit()
        self.reg_email    = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_name.setPlaceholderText("Full Name")
        self.reg_email.setPlaceholderText("your@email.com")
        self.reg_password.setPlaceholderText("Min 6 characters")

        form.addRow("Full Name:", self.reg_name)
        form.addRow("Email:",     self.reg_email)
        form.addRow("Password:",  self.reg_password)
        layout.addLayout(form)

        btn_register = QPushButton("Create Account")
        btn_register.setFixedHeight(36)
        btn_register.setStyleSheet("background-color: #16A34A; color: white; border-radius: 4px; font-weight: bold;")
        btn_register.clicked.connect(self._handle_register)
        layout.addWidget(btn_register)

        layout.addStretch()
        return widget

    def _handle_register(self):
        success, msg = models.register_citizen(
            self.reg_name.text(),
            self.reg_email.text(),
            self.reg_password.text()
        )
        if success:
            QMessageBox.information(self, "Success", msg + "\nYou can now login.")
            self.reg_name.clear()
            self.reg_email.clear()
            self.reg_password.clear()
        else:
            QMessageBox.warning(self, "Registration Failed", msg)
