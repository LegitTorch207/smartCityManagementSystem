# Smart City Management System - Field Worker Dashboard
# Features: View assigned tasks, Update task status

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QMessageBox, QFormLayout,
    QHeaderView, QGroupBox
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


class WorkerDashboard(QMainWindow):
    """
    Dashboard for field workers.
    Shows their assigned tasks and lets them update task status.
    """

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Worker Dashboard — {user['name']}")
        self.setMinimumSize(750, 500)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout  = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top bar
        top = QHBoxLayout()
        title = QLabel("🔧 Field Worker Dashboard")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        top.addWidget(title)
        top.addStretch()
        welcome = QLabel(f"Worker: {self.user['name']}")
        welcome.setStyleSheet("color: #475569;")
        top.addWidget(welcome)
        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("color: red;")
        btn_logout.clicked.connect(self._logout)
        top.addWidget(btn_logout)
        layout.addLayout(top)

        # Info bar
        info = QLabel(
            "ℹ️ Below are all tasks assigned to you. Update status as you progress: "
            "Pending → In Progress → Completed"
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background-color: #EFF6FF; border: 1px solid #BFDBFE; "
            "border-radius: 4px; padding: 8px; color: #1E40AF; font-size: 11px;"
        )
        layout.addWidget(info)

        # Refresh button
        btn_refresh = QPushButton("Refresh My Tasks")
        btn_refresh.setIcon(QIcon("icons/refresh.png"))
        btn_refresh.setFixedWidth(170)
        btn_refresh.clicked.connect(self._load_tasks)
        layout.addWidget(btn_refresh)

        # Tasks table
        self.tasks_table = QTableWidget()
        self._load_tasks()
        layout.addWidget(self.tasks_table)

        # Update status panel
        update_box = QGroupBox("Update Task Status")
        form = QFormLayout(update_box)

        self.task_id_input = QLineEdit()
        self.task_id_input.setPlaceholderText("Enter Task ID from table above")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["In Progress", "Completed"])

        btn_update = QPushButton("Update Status")
        btn_update.setFixedHeight(34)
        btn_update.setStyleSheet(
            "background-color: #2563EB; color: white; border-radius: 4px; font-weight: bold;"
        )
        btn_update.clicked.connect(self._update_status)

        form.addRow("Task ID:",    self.task_id_input)
        form.addRow("New Status:", self.status_combo)
        form.addRow("",            btn_update)

        layout.addWidget(update_box)

    # Load Tasks

    def _load_tasks(self):
        data    = models.get_worker_tasks(self.user['id'])
        headers = ["Task ID", "Complaint Description", "Complaint Status", "My Task Status", "Assigned At"]
        keys    = ["id", "description", "complaint_status", "task_status", "assigned_at"]
        populate_table(self.tasks_table, headers, data, keys)

        # Color-code task status column (index 3)
        for row in range(self.tasks_table.rowCount()):
            status_item = self.tasks_table.item(row, 3)
            if status_item:
                status = status_item.text()
                if status == 'Completed':
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                elif status == 'In Progress':
                    status_item.setForeground(Qt.GlobalColor.darkBlue)
                else:  # Pending
                    status_item.setForeground(Qt.GlobalColor.darkRed)

    # Update Task Status

    def _update_status(self):
        task_id_text = self.task_id_input.text().strip()
        if not task_id_text:
            QMessageBox.warning(self, "Error", "Please enter a Task ID.")
            return

        try:
            task_id = int(task_id_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Task ID must be a number.")
            return

        new_status = self.status_combo.currentText()

        # Validate the task belongs to this worker
        tasks = models.get_worker_tasks(self.user['id'])
        task  = next((t for t in tasks if t['id'] == task_id), None)

        if not task:
            QMessageBox.warning(self, "Error", "Task not found in your task list.")
            return

        if task['task_status'] == 'Completed':
            QMessageBox.information(self, "Info", "This task is already marked Completed.")
            return

        ok, msg = models.update_task(task_id, new_status)
        QMessageBox.information(self, "Updated", msg)
        self.task_id_input.clear()
        self._load_tasks()

    # Logout

    def _logout(self):
        from ui_login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()
