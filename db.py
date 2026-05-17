# db.py
# ============================================================
# Smart City Management System - Database Connection Layer
# Handles all raw SQL queries via pyodbc
# ============================================================

import pyodbc

# ============================================================
# DATABASE CONFIGURATION
# Update SERVER to your MS SQL Server instance name.
# Common values:
#   'localhost'               -> default local instance
#   'localhost\\SQLEXPRESS'   -> SQL Server Express
#   '.\\SQLEXPRESS'           -> shorthand for Express
# ============================================================
SERVER   = 'localhost\\SQLEXPRESS'   # <-- Change this if needed
DATABASE = 'SmartCityDB'

def get_connection():
    """
    Create and return a pyodbc connection to the MS SQL database.
    Uses Windows Authentication (Trusted_Connection).
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


# ============================================================
# AUTHENTICATION QUERIES
# ============================================================

def login_citizen(email, password):
    """Return citizen row if credentials match, else None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email FROM citizens WHERE email=? AND password=?",
        (email, password)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def login_employee(email, password):
    """Return employee row (id, name, role, dept) if credentials match."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, role, department_id FROM employees WHERE email=? AND password=?",
        (email, password)
    )
    row = cursor.fetchone()
    conn.close()
    return row


# ============================================================
# CITIZEN QUERIES
# ============================================================

def register_citizen(name, email, password):
    """Insert a new citizen. Returns True on success, False if email exists."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO citizens (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except pyodbc.IntegrityError:
        return False  # Duplicate email


def get_citizen_complaints(citizen_id):
    """Return all complaints submitted by a citizen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.description, c.status, ISNULL(d.name, 'Not Assigned') AS department, c.created_at
        FROM complaints c
        LEFT JOIN departments d ON c.department_id = d.id
        WHERE c.citizen_id = ?
        ORDER BY c.created_at DESC
    """, (citizen_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def submit_complaint(citizen_id, description):
    """Insert a new complaint with Pending status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (citizen_id, description) VALUES (?, ?)",
        (citizen_id, description)
    )
    conn.commit()
    conn.close()


def get_citizen_utilities(citizen_id):
    """Return all utility bills for a citizen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, type, usage_units, bill_amount, bill_month,
               CASE is_paid WHEN 1 THEN 'Paid' ELSE 'Unpaid' END AS status
        FROM utilities
        WHERE citizen_id = ?
        ORDER BY id DESC
    """, (citizen_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def pay_utility_bill(citizen_id, utility_id, amount):
    """Mark utility as paid and record payment."""
    conn = get_connection()
    cursor = conn.cursor()
    # Mark bill as paid
    cursor.execute(
        "UPDATE utilities SET is_paid = 1 WHERE id = ? AND citizen_id = ?",
        (utility_id, citizen_id)
    )
    # Record payment
    cursor.execute(
        "INSERT INTO payments (citizen_id, utility_id, amount) VALUES (?, ?, ?)",
        (citizen_id, utility_id, amount)
    )
    conn.commit()
    conn.close()


# ============================================================
# ADMIN QUERIES
# ============================================================

def get_all_complaints():
    """Return all complaints with citizen name and department."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, ci.name AS citizen, c.description, c.status,
               ISNULL(d.name, 'Not Assigned') AS department, c.created_at
        FROM complaints c
        JOIN citizens ci ON c.citizen_id = ci.id
        LEFT JOIN departments d ON c.department_id = d.id
        ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_departments():
    """Return list of all departments."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM departments ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def assign_complaint_to_department(complaint_id, department_id):
    """Assign a complaint to a department and update status to Assigned."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE complaints SET department_id=?, status='Assigned' WHERE id=?",
        (department_id, complaint_id)
    )
    conn.commit()
    conn.close()


def get_workers():
    """Return all field workers (role = Worker)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.name, ISNULL(d.name, 'N/A') AS department
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.role = 'Worker'
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def assign_task_to_worker(complaint_id, employee_id):
    """Create a task linking complaint to a worker."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (complaint_id, employee_id) VALUES (?, ?)",
        (complaint_id, employee_id)
    )
    # Update complaint status
    cursor.execute(
        "UPDATE complaints SET status='In Progress' WHERE id=?",
        (complaint_id,)
    )
    conn.commit()
    conn.close()


def get_all_employees():
    """Return all employees with their department name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.name, e.email, e.role, ISNULL(d.name, 'N/A') AS department
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        ORDER BY e.role
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_employee(name, email, password, role, department_id):
    """Insert a new employee. Returns True on success."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        dept = department_id if department_id else None
        cursor.execute(
            "INSERT INTO employees (name, email, password, role, department_id) VALUES (?,?,?,?,?)",
            (name, email, password, role, dept)
        )
        conn.commit()
        conn.close()
        return True
    except pyodbc.IntegrityError:
        return False


def add_utility_bill(citizen_id, utility_type, usage_units, bill_amount, bill_month):
    """Insert a utility bill for a citizen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO utilities (citizen_id, type, usage_units, bill_amount, bill_month) VALUES (?,?,?,?,?)",
        (citizen_id, utility_type, usage_units, bill_amount, bill_month)
    )
    conn.commit()
    conn.close()


def get_all_citizens():
    """Return all citizens (for admin utility bill management)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM citizens ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_utilities():
    """Return all utility bills with citizen names."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, ci.name, u.type, u.usage_units, u.bill_amount, u.bill_month,
               CASE u.is_paid WHEN 1 THEN 'Paid' ELSE 'Unpaid' END AS status
        FROM utilities u
        JOIN citizens ci ON u.citizen_id = ci.id
        ORDER BY u.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ============================================================
# WORKER QUERIES
# ============================================================

def get_worker_tasks(employee_id):
    """Return all tasks assigned to a specific worker."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, c.description, c.status AS complaint_status,
               t.status AS task_status, t.assigned_at
        FROM tasks t
        JOIN complaints c ON t.complaint_id = c.id
        WHERE t.employee_id = ?
        ORDER BY t.assigned_at DESC
    """, (employee_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_task_status(task_id, new_status):
    """Update the status of a task. Also updates complaint if completed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status=? WHERE id=?",
        (new_status, task_id)
    )
    # If task completed, also mark complaint completed
    if new_status == 'Completed':
        cursor.execute("""
            UPDATE complaints SET status='Completed'
            WHERE id = (SELECT complaint_id FROM tasks WHERE id=?)
        """, (task_id,))
    conn.commit()
    conn.close()
