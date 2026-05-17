# ============================================================
# Smart City Management System
# README - Setup & Run Instructions
# ============================================================

## PROJECT STRUCTURE
```
SmartCity/
├── main.py           # Entry point — run this
├── db.py             # Database connection & raw SQL queries
├── models.py         # Business logic layer
├── ui_login.py       # Login & Registration window
├── ui_admin.py       # Admin / Officer dashboard
├── ui_citizen.py     # Citizen dashboard
├── ui_worker.py      # Field Worker dashboard
├── schema.sql        # MS SQL database setup script
└── README.md         # This file
```

---

## PREREQUISITES

### 1. Python 3.10+
Download: https://www.python.org/downloads/

### 2. Microsoft SQL Server
- SQL Server Express (free): https://www.microsoft.com/en-us/sql-server/sql-server-downloads
- SQL Server Management Studio (SSMS): https://aka.ms/ssms

### 3. ODBC Driver 17 for SQL Server
Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

---

## PYTHON DEPENDENCIES

Install via pip:
```
pip install PyQt6 pyodbc
```

---

## DATABASE SETUP

### Step 1: Open SSMS
Connect to your SQL Server instance.

### Step 2: Run schema.sql
Open `schema.sql` in SSMS and click Execute (F5).
This creates:
- Database: SmartCityDB
- All 7 tables with relationships
- Seed data (demo accounts + departments)

### Step 3: Update db.py
Edit the SERVER variable in db.py:
```python
SERVER = 'localhost\\SQLEXPRESS'   # for SQL Server Express
# OR
SERVER = 'localhost'               # for default SQL Server
# OR
SERVER = '.\\SQLEXPRESS'           # shorthand
```

---

## RUNNING THE APPLICATION

```bash
cd SmartCity
python main.py
```

---

## DEMO ACCOUNTS

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Admin   | admin@city.gov         | admin123   |
| Officer | officer@city.gov       | officer123 |
| Worker  | worker@city.gov        | worker123  |
| Citizen | citizen@gmail.com      | citizen123 |

Or register a new Citizen account from the Login → Register tab.

---

## WORKFLOW DEMO

### Complaint Flow (end-to-end):
1. **Login as Citizen** → Submit a complaint
2. **Login as Admin** → Go to Complaints tab
   - Enter the Complaint ID
   - Assign a Department → click "Assign Department"
   - Select a Worker → click "Assign to Worker"
3. **Login as Worker** → See the task in My Tasks
   - Enter Task ID → change status to "In Progress" → Update
   - Later: change to "Completed" → this closes the complaint

### Utility Bills:
1. **Login as Admin** → Go to Utility Bills tab
   - Select a citizen, type, usage, rate, month → Generate Bill
2. **Login as Citizen** → Go to My Utility Bills
   - Enter Bill ID → Pay Bill

---

## DATABASE TABLES

| Table       | Description                              |
|-------------|------------------------------------------|
| citizens    | Registered city residents                |
| employees   | City staff (Admin, Officer, Worker)      |
| departments | City departments (Water, Traffic, etc.)  |
| complaints  | Issues submitted by citizens             |
| tasks       | Work orders assigned to field workers    |
| utilities   | Monthly utility bills per citizen        |
| payments    | Payment records for utility bills        |

---

## TROUBLESHOOTING

**Error: "Data source name not found"**
→ ODBC Driver 17 not installed. Download from Microsoft link above.

**Error: "Login failed"**
→ Check SERVER name in db.py. Try both 'localhost\\SQLEXPRESS' and 'localhost'.

**Error: "Cannot open database SmartCityDB"**
→ Run schema.sql first in SSMS.

**App not launching:**
→ Run: pip install PyQt6 pyodbc

---

## NOTES FOR STUDENTS

- Passwords stored in plain text for simplicity (lab project only).
  In production, use bcrypt or similar hashing.
- The app uses Windows Authentication (Trusted_Connection).
  To use SQL username/password, update get_connection() in db.py.
- All queries are in db.py — study them to understand SQL integration.
- models.py acts as a service/controller layer between UI and DB.
