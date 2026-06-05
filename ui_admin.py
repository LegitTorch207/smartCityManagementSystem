# Smart City Management System - Admin / Officer Dashboard
# Features: Complaints, Employee Management, Utility Billing

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QLineEdit, QComboBox, QMessageBox,
    QFormLayout, QHeaderView, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QIcon

import models

# HELPER: Populate a QTableWidget from list-of-dicts

def populate_table(table: QTableWidget, headers: list, rows: list, keys: list):
    """Generic table fill from list of dicts."""
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setRowCount(len(rows))
    for r_idx, row in enumerate(rows):
        for c_idx, key in enumerate(keys):
            val = str(row.get(key, ''))
            item = QTableWidgetItem(val)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(r_idx, c_idx, item)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class AdminDashboard(QMainWindow):
    """
    Dashboard for Admin and Officer roles.
    Tabs: Complaints | Employees | Utility Bills
    """

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Admin Dashboard — {user['name']} ({user['role']})")
        self.setMinimumSize(900, 600)
        self._build_ui()

    def _build_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top bar
        top = QHBoxLayout()
        title = QLabel(f"🏙️ Smart City — {self.user['role']} Panel")
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

        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._build_complaints_tab(), "📋 Complaints")
        tabs.addTab(self._build_employees_tab(), "👥 Employees")
        tabs.addTab(self._build_utilities_tab(), "💡 Utility Bills")
        layout.addWidget(tabs)


    # COMPLAINTS TAB

    def _build_complaints_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Refresh button
        btn_refresh = QPushButton("Refresh Complaints")
        btn_refresh.setIcon(QIcon("icons/refresh.png")) 
        btn_refresh.setFixedWidth(180)
        btn_refresh.clicked.connect(self._load_complaints)
        layout.addWidget(btn_refresh)

        # Complaints table
        self.complaints_table = QTableWidget()
        self._load_complaints()
        layout.addWidget(self.complaints_table)

        # Action panel
        action_box = QGroupBox("Assign Complaint")
        action_layout = QFormLayout(action_box)

        self.complaint_id_input = QLineEdit()
        self.complaint_id_input.setPlaceholderText("Enter Complaint ID from table")

        # Department dropdown
        self.dept_combo = QComboBox()
        self._load_departments_combo()

        # Worker dropdown
        self.worker_combo = QComboBox()
        self._load_workers_combo()

        btn_assign_dept   = QPushButton("Assign Department")
        btn_assign_worker = QPushButton("Assign to Worker")
        btn_assign_dept.setStyleSheet("background-color: #2563EB; color: white;")
        btn_assign_worker.setStyleSheet("background-color: #7C3AED; color: white;")
        btn_assign_dept.clicked.connect(self._assign_department)
        btn_assign_worker.clicked.connect(self._assign_worker)

        action_layout.addRow("Complaint ID:", self.complaint_id_input)
        action_layout.addRow("Department:",   self.dept_combo)
        action_layout.addRow("",              btn_assign_dept)
        action_layout.addRow("Worker:",       self.worker_combo)
        action_layout.addRow("",              btn_assign_worker)

        layout.addWidget(action_box)
        return widget

    def _load_complaints(self):
        data = models.get_all_complaints()
        headers = ["ID", "Citizen", "Description", "Status", "Department", "Date"]
        keys    = ["id", "citizen", "description", "status", "department", "created_at"]
        populate_table(self.complaints_table, headers, data, keys)

    def _load_departments_combo(self):
        self.dept_combo.clear()
        self._departments = models.get_departments()
        for d in self._departments:
            self.dept_combo.addItem(d['name'], d['id'])

    def _load_workers_combo(self):
        self.worker_combo.clear()
        self._workers = models.get_workers()
        for w in self._workers:
            self.worker_combo.addItem(f"{w['name']} ({w['department']})", w['id'])

    def _assign_department(self):
        complaint_id  = self.complaint_id_input.text().strip()
        department_id = self.dept_combo.currentData()
        if not complaint_id:
            QMessageBox.warning(self, "Error", "Please enter a Complaint ID.")
            return
        ok, msg = models.assign_department(int(complaint_id), department_id)
        QMessageBox.information(self, "Result", msg)
        self._load_complaints()

    def _assign_worker(self):
        complaint_id = self.complaint_id_input.text().strip()
        employee_id  = self.worker_combo.currentData()
        if not complaint_id:
            QMessageBox.warning(self, "Error", "Please enter a Complaint ID.")
            return
        if not employee_id:
            QMessageBox.warning(self, "Error", "No workers available.")
            return
        ok, msg = models.assign_worker(int(complaint_id), employee_id)
        QMessageBox.information(self, "Result", msg)
        self._load_complaints()


    # EMPLOYEES TAB

    def _build_employees_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_refresh = QPushButton("Refresh Employees")
        btn_refresh.setIcon(QIcon("icons/refresh.png")) 
        btn_refresh.setFixedWidth(180)
        btn_refresh.clicked.connect(self._load_employees)
        layout.addWidget(btn_refresh)

        self.employees_table = QTableWidget()
        self._load_employees()
        layout.addWidget(self.employees_table)

        # Add employee form
        add_box = QGroupBox("Add New Employee")
        form = QFormLayout(add_box)

        self.emp_name   = QLineEdit()
        self.emp_email  = QLineEdit()
        self.emp_pass   = QLineEdit()
        self.emp_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.emp_role   = QComboBox()
        self.emp_role.addItems(["Admin", "Officer", "Worker"])
        self.emp_dept   = QComboBox()
        self._load_emp_dept_combo()

        btn_add = QPushButton("Add Employee")
        btn_add.setStyleSheet("background-color: #16A34A; color: white;")
        btn_add.clicked.connect(self._add_employee)

        form.addRow("Name:",       self.emp_name)
        form.addRow("Email:",      self.emp_email)
        form.addRow("Password:",   self.emp_pass)
        form.addRow("Role:",       self.emp_role)
        form.addRow("Department:", self.emp_dept)
        form.addRow("",            btn_add)

        layout.addWidget(add_box)
        return widget

    def _load_employees(self):
        data    = models.get_all_employees()
        headers = ["ID", "Name", "Email", "Role", "Department"]
        keys    = ["id", "name", "email", "role", "department"]
        populate_table(self.employees_table, headers, data, keys)

    def _load_emp_dept_combo(self):
        self.emp_dept.clear()
        self.emp_dept.addItem("None (Admin)", None)
        for d in models.get_departments():
            self.emp_dept.addItem(d['name'], d['id'])

    def _add_employee(self):
        ok, msg = models.add_employee(
            self.emp_name.text(),
            self.emp_email.text(),
            self.emp_pass.text(),
            self.emp_role.currentText(),
            self.emp_dept.currentData()
        )
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.emp_name.clear()
            self.emp_email.clear()
            self.emp_pass.clear()
            self._load_employees()
        else:
            QMessageBox.warning(self, "Error", msg)


    # UTILITY BILLS TAB

    def _build_utilities_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        btn_refresh = QPushButton("Refresh Utility Bills")
        btn_refresh.setIcon(QIcon("icons/refresh.png")) 
        btn_refresh.setFixedWidth(150)
        btn_refresh.clicked.connect(self._load_utilities)
        layout.addWidget(btn_refresh)

        self.utilities_table = QTableWidget()
        self._load_utilities()
        layout.addWidget(self.utilities_table)

        # Generate bill form
        gen_box = QGroupBox("Generate Utility Bill")
        form    = QFormLayout(gen_box)

        self.bill_citizen  = QComboBox()
        self._load_citizens_combo()
        self.bill_type     = QComboBox()
        self.bill_type.addItems(["Water", "Gas", "Electricity"])
        self.bill_usage    = QLineEdit()
        self.bill_rate     = QLineEdit()
        self.bill_month    = QLineEdit()
        self.bill_usage.setPlaceholderText("e.g. 120")
        self.bill_rate.setPlaceholderText("e.g. 25.5 (per unit)")
        self.bill_month.setPlaceholderText("e.g. June 2025")

        btn_gen = QPushButton("Generate Bill")
        btn_gen.setStyleSheet("background-color: #D97706; color: white;")
        btn_gen.clicked.connect(self._generate_bill)

        form.addRow("Citizen:",    self.bill_citizen)
        form.addRow("Type:",       self.bill_type)
        form.addRow("Usage Units:",self.bill_usage)
        form.addRow("Rate/Unit:",  self.bill_rate)
        form.addRow("Month:",      self.bill_month)
        form.addRow("",            btn_gen)

        layout.addWidget(gen_box)
        return widget

    def _load_utilities(self):
        data    = models.get_all_utilities()
        headers = ["ID", "Citizen", "Type", "Usage", "Amount", "Month", "Status"]
        keys    = ["id", "citizen", "type", "usage", "amount", "month", "status"]
        populate_table(self.utilities_table, headers, data, keys)

    def _load_citizens_combo(self):
        self.bill_citizen.clear()
        self._citizens = models.get_all_citizens()
        for c in self._citizens:
            self.bill_citizen.addItem(f"{c['name']} ({c['email']})", c['id'])

    def _generate_bill(self):
        citizen_id = self.bill_citizen.currentData()
        ok, msg = models.add_utility_bill(
            citizen_id,
            self.bill_type.currentText(),
            self.bill_usage.text(),
            self.bill_rate.text(),
            self.bill_month.text()
        )
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.bill_usage.clear()
            self.bill_rate.clear()
            self.bill_month.clear()
            self._load_utilities()
        else:
            QMessageBox.warning(self, "Error", msg)


    # LOGOUT

    def _logout(self):
        from ui_login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()