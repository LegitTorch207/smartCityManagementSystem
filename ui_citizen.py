# Smart City Management System - Citizen Dashboard
# Features: Submit Complaint, View Complaints, Utility Bills

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QLineEdit, QTextEdit, QMessageBox,
    QFormLayout, QHeaderView, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QIcon

import models


def populate_table(table, headers, rows, keys):
    """Generic table fill helper."""
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for r_idx, row in enumerate(rows):
        for c_idx, key in enumerate(keys):
            val  = str(row.get(key, ''))
            item = QTableWidgetItem(val)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(r_idx, c_idx, item)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class CitizenDashboard(QMainWindow):
    """
    Dashboard for logged-in citizens.
    Tabs: My Complaints | Submit Complaint | My Bills
    """

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Citizen Portal — {user['name']}")
        self.setMinimumSize(800, 550)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout  = QVBoxLayout(central)

        # Top bar
        top = QHBoxLayout()
        title = QLabel("🏙️ Smart City — Citizen Portal")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        top.addWidget(title)
        top.addStretch()
        welcome = QLabel(f"Welcome, {self.user['name']}")
        welcome.setStyleSheet("color: #475569;")
        top.addWidget(welcome)
        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("color: red;")
        btn_logout.clicked.connect(self._logout)
        top.addWidget(btn_logout)
        layout.addLayout(top)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_complaints_tab(), "📋 My Complaints")
        tabs.addTab(self._build_submit_tab(),     "✏️ Submit Complaint")
        tabs.addTab(self._build_bills_tab(),      "💡 My Utility Bills")
        layout.addWidget(tabs)

    
    # MY COMPLAINTS TAB

    def _build_complaints_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_refresh = QPushButton("Refresh Complaints")
        btn_refresh.setIcon(QIcon("icons/refresh.png")) 
        btn_refresh.setFixedWidth(120)
        btn_refresh.clicked.connect(self._load_complaints)
        layout.addWidget(btn_refresh)

        self.complaints_table = QTableWidget()
        self._load_complaints()
        layout.addWidget(self.complaints_table)

        note = QLabel("ℹ️ Status updates from Pending → Assigned → In Progress → Completed as the city handles your complaint.")
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

        return widget

    def _load_complaints(self):
        data    = models.get_citizen_complaints(self.user['id'])
        headers = ["ID", "Description", "Status", "Department", "Submitted"]
        keys    = ["id", "description", "status", "department", "created_at"]
        populate_table(self.complaints_table, headers, data, keys)

    # SUBMIT COMPLAINT TAB

    def _build_submit_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel("Describe your issue in detail:")
        label.setFont(QFont("Arial", 11))
        layout.addWidget(label)

        self.complaint_text = QTextEdit()
        self.complaint_text.setPlaceholderText(
            "Example: There is a broken streetlight on Main Street near Civic Center. "
            "It has been dark for 3 days causing safety issues..."
        )
        self.complaint_text.setFixedHeight(150)
        layout.addWidget(self.complaint_text)

        btn_submit = QPushButton("Submit Complaint")
        btn_submit.setFixedHeight(38)
        btn_submit.setStyleSheet(
            "background-color: #2563EB; color: white; border-radius: 4px; font-weight: bold;"
        )
        btn_submit.clicked.connect(self._submit_complaint)
        layout.addWidget(btn_submit)

        self.submit_status = QLabel("")
        self.submit_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.submit_status)

        layout.addStretch()
        return widget

    def _submit_complaint(self):
        description = self.complaint_text.toPlainText().strip()
        ok, msg = models.submit_complaint(self.user['id'], description)
        if ok:
            self.submit_status.setStyleSheet("color: green;")
            self.submit_status.setText("✅ " + msg)
            self.complaint_text.clear()
            self._load_complaints()   # refresh the My Complaints tab
        else:
            self.submit_status.setStyleSheet("color: red;")
            self.submit_status.setText("❌ " + msg)

    # MY UTILITY BILLS TAB

    def _build_bills_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_refresh = QPushButton("Refresh Bills")
        btn_refresh.setIcon(QIcon("icons/refresh.png"))
        btn_refresh.setFixedWidth(140)
        btn_refresh.clicked.connect(self._load_bills)
        layout.addWidget(btn_refresh)

        self.bills_table = QTableWidget()
        self._load_bills()
        layout.addWidget(self.bills_table)

        # Pay bill section
        pay_box = QGroupBox("Pay a Bill")
        form    = QFormLayout(pay_box)

        self.bill_id_input = QLineEdit()
        self.bill_id_input.setPlaceholderText("Enter Bill ID from table above")

        btn_pay = QPushButton("Pay Bill")
        btn_pay.setStyleSheet("background-color: #16A34A; color: white;")
        btn_pay.clicked.connect(self._pay_bill)

        form.addRow("Bill ID:", self.bill_id_input)
        form.addRow("",         btn_pay)

        layout.addWidget(pay_box)
        return widget

    def _load_bills(self):
        data    = models.get_citizen_utilities(self.user['id'])
        headers = ["ID", "Type", "Usage (Units)", "Amount", "Month", "Status"]
        keys    = ["id", "type", "usage", "amount", "month", "status"]
        populate_table(self.bills_table, headers, data, keys)

    def _pay_bill(self):
        bill_id_text = self.bill_id_input.text().strip()
        if not bill_id_text:
            QMessageBox.warning(self, "Error", "Please enter a Bill ID.")
            return

        try:
            bill_id = int(bill_id_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Bill ID must be a number.")
            return

        # Find the bill in the current citizen's bills
        bills = models.get_citizen_utilities(self.user['id'])
        bill  = next((b for b in bills if b['id'] == bill_id), None)

        if not bill:
            QMessageBox.warning(self, "Error", "Bill not found for your account.")
            return

        if bill['status'] == 'Paid':
            QMessageBox.information(self, "Info", "This bill is already paid.")
            return

        ok, msg = models.pay_bill(self.user['id'], bill_id, bill['bill_amount'])
        QMessageBox.information(self, "Payment", msg)
        self.bill_id_input.clear()
        self._load_bills()

    # LOGOUT

    def _logout(self):
        from ui_login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()
