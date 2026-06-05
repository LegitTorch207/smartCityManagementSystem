# Smart City Management System - Business Logic / Models
# Acts as a bridge between UI and database layer (db.py)
# Keeps validation and formatting logic separate from UI

import db

# AUTHENTICATION

def authenticate(email, password, user_type):
    """
    Authenticate a user based on type ('citizen' or 'employee').
    Returns a dict with user info and role, or None on failure.
    """
    email    = email.strip()
    password = password.strip()

    if user_type == 'citizen':
        row = db.login_citizen(email, password)
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2], 'role': 'Citizen'}

    elif user_type == 'employee':
        row = db.login_employee(email, password)
        if row:
            return {
                'id':            row[0],
                'name':          row[1],
                'role':          row[2],       # Admin / Officer / Worker
                'department_id': row[3]
            }

    return None


def register_citizen(name, email, password):
    """
    Register a new citizen after basic validation.
    Returns (True, '') on success or (False, error_message) on failure.
    """
    if not name or not email or not password:
        return False, "All fields are required."
    if '@' not in email:
        return False, "Invalid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    success = db.register_citizen(name.strip(), email.strip(), password)
    if success:
        return True, "Registration successful!"
    return False, "Email already registered. Please login."

# COMPLAINT MANAGEMENT

def get_citizen_complaints(citizen_id):
    """Return complaint list as list of dicts for easy UI binding."""
    rows = db.get_citizen_complaints(citizen_id)
    return [
        {
            'id':          r[0],
            'description': r[1],
            'status':      r[2],
            'department':  r[3],
            'created_at':  str(r[4])[:16]   # Trim seconds
        }
        for r in rows
    ]


def submit_complaint(citizen_id, description):
    """Submit a complaint after validating description."""
    if not description or len(description.strip()) < 10:
        return False, "Please enter a description (at least 10 characters)."
    db.submit_complaint(citizen_id, description.strip())
    return True, "Complaint submitted successfully!"


def get_all_complaints():
    """Return all complaints for admin/officer view."""
    rows = db.get_all_complaints()
    return [
        {
            'id':          r[0],
            'citizen':     r[1],
            'description': r[2],
            'status':      r[3],
            'department':  r[4],
            'created_at':  str(r[5])[:16]
        }
        for r in rows
    ]


def assign_department(complaint_id, department_id):
    """Assign a department to a complaint."""
    db.assign_complaint_to_department(complaint_id, department_id)
    return True, "Department assigned successfully!"


def assign_worker(complaint_id, employee_id):
    """Assign a task to a worker for a given complaint."""
    db.assign_task_to_worker(complaint_id, employee_id)
    return True, "Task assigned to worker!"


def get_departments():
    """Return departments as list of dicts."""
    rows = db.get_all_departments()
    return [{'id': r[0], 'name': r[1]} for r in rows]


def get_workers():
    """Return workers as list of dicts."""
    rows = db.get_workers()
    return [{'id': r[0], 'name': r[1], 'department': r[2]} for r in rows]

# EMPLOYEE MANAGEMENT

def get_all_employees():
    """Return employees as list of dicts."""
    rows = db.get_all_employees()
    return [
        {
            'id':         r[0],
            'name':       r[1],
            'email':      r[2],
            'role':       r[3],
            'department': r[4]
        }
        for r in rows
    ]


def add_employee(name, email, password, role, department_id):
    """Add a new employee with basic validation."""
    if not name or not email or not password or not role:
        return False, "All fields are required."
    success = db.add_employee(name, email, password, role, department_id)
    if success:
        return True, "Employee added successfully!"
    return False, "Email already exists."


# UTILITY BILLING

def get_citizen_utilities(citizen_id):
    """Return utilities for a citizen as list of dicts."""
    rows = db.get_citizen_utilities(citizen_id)
    return [
        {
            'id':          r[0],
            'type':        r[1],
            'usage':       r[2],
            'amount':      f"PKR {r[3]:,.2f}",
            'bill_amount': r[3],
            'month':       r[4],
            'status':      r[5]
        }
        for r in rows
    ]


def pay_bill(citizen_id, utility_id, amount):
    """Process a utility bill payment."""
    db.pay_utility_bill(citizen_id, utility_id, amount)
    return True, "Payment recorded successfully!"


def add_utility_bill(citizen_id, utility_type, usage_units, rate_per_unit, bill_month):
    """
    Generate a bill for a citizen.
    Bill amount = usage_units * rate_per_unit
    """
    if not citizen_id or not utility_type or not usage_units or not bill_month:
        return False, "All fields are required."
    try:
        usage   = float(usage_units)
        rate    = float(rate_per_unit)
        amount  = round(usage * rate, 2)
        db.add_utility_bill(citizen_id, utility_type, usage, amount, bill_month)
        return True, f"Bill of PKR {amount:,.2f} generated!"
    except ValueError:
        return False, "Usage and rate must be numeric."


def get_all_citizens():
    """Return all citizens."""
    rows = db.get_all_citizens()
    return [{'id': r[0], 'name': r[1], 'email': r[2]} for r in rows]


def get_all_utilities():
    """Return all utility bills (for admin view)."""
    rows = db.get_all_utilities()
    return [
        {
            'id':       r[0],
            'citizen':  r[1],
            'type':     r[2],
            'usage':    r[3],
            'amount':   f"PKR {r[4]:,.2f}",
            'month':    r[5],
            'status':   r[6]
        }
        for r in rows
    ]

# WORKER TASKS

def get_worker_tasks(employee_id):
    """Return task list for a worker."""
    rows = db.get_worker_tasks(employee_id)
    return [
        {
            'id':               r[0],
            'description':      r[1],
            'complaint_status': r[2],
            'task_status':      r[3],
            'assigned_at':      str(r[4])[:16]
        }
        for r in rows
    ]


def update_task(task_id, new_status):
    """Update task status."""
    db.update_task_status(task_id, new_status)
    return True, f"Task status updated to '{new_status}'!"
