-- Smart City Management System - Database Schema
-- MS SQL Server Script

-- Create and use the database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SmartCityDB')
    CREATE DATABASE SmartCityDB;
GO

USE SmartCityDB;
GO

-- TABLE: departments
-- Stores city departments (e.g., Water, Traffic, Waste)

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='departments' AND xtype='U')
CREATE TABLE departments (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE
);
GO

-- TABLE: citizens
-- Stores registered citizens who can submit complaints/pay bills

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='citizens' AND xtype='U')
CREATE TABLE citizens (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    password    VARCHAR(100) NOT NULL   
);
GO

-- TABLE: employees
-- Stores all city employees (Admin, Officers, Field Workers)

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='employees' AND xtype='U')
CREATE TABLE employees (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password        VARCHAR(100) NOT NULL,
    role            VARCHAR(50)  NOT NULL CHECK (role IN ('Admin', 'Officer', 'Worker')),
    department_id   INT REFERENCES departments(id)
);
GO

-- TABLE: complaints
-- Citizen-submitted complaints tracked through departments

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='complaints' AND xtype='U')
CREATE TABLE complaints (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    citizen_id      INT NOT NULL REFERENCES citizens(id),
    description     VARCHAR(500) NOT NULL,
    status          VARCHAR(50)  NOT NULL DEFAULT 'Pending'
                        CHECK (status IN ('Pending', 'Assigned', 'In Progress', 'Completed')),
    department_id   INT REFERENCES departments(id),
    created_at      DATETIME DEFAULT GETDATE()
);
GO

-- TABLE: tasks
-- Tasks assigned to field workers based on complaints

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
CREATE TABLE tasks (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    complaint_id    INT NOT NULL REFERENCES complaints(id),
    employee_id     INT NOT NULL REFERENCES employees(id),
    status          VARCHAR(50) NOT NULL DEFAULT 'Pending'
                        CHECK (status IN ('Pending', 'In Progress', 'Completed')),
    assigned_at     DATETIME DEFAULT GETDATE()
);
GO

-- TABLE: utilities
-- Tracks utility usage per citizen (Water, Gas, Electricity)

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='utilities' AND xtype='U')
CREATE TABLE utilities (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    citizen_id      INT NOT NULL REFERENCES citizens(id),
    type            VARCHAR(50) NOT NULL CHECK (type IN ('Water', 'Gas', 'Electricity')),
    usage_units     FLOAT NOT NULL,
    bill_amount     DECIMAL(10, 2) NOT NULL,
    bill_month      VARCHAR(20) NOT NULL,   -- e.g., 'June 2025'
    is_paid         BIT NOT NULL DEFAULT 0
);
GO

-- TABLE: payments
-- Records payments made by citizens for utility bills

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='payments' AND xtype='U')
CREATE TABLE payments (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    citizen_id      INT NOT NULL REFERENCES citizens(id),
    utility_id      INT NOT NULL REFERENCES utilities(id),
    amount          DECIMAL(10, 2) NOT NULL,
    paid_at         DATETIME DEFAULT GETDATE()
);
GO

-- SEED DATA: Insert default departments

IF NOT EXISTS (SELECT * FROM departments WHERE name = 'Water Supply')
BEGIN
    INSERT INTO departments (name) VALUES
        ('Water Supply'),
        ('Waste Management'),
        ('Traffic Control'),
        ('Electricity'),
        ('Emergency Services');
END
GO

-- SEED DATA: Insert default Admin account
-- Email: admin@city.gov | Password: admin123

IF NOT EXISTS (SELECT * FROM employees WHERE email = 'admin@city.gov')
BEGIN
    INSERT INTO employees (name, email, password, role, department_id)
    VALUES ('City Admin', 'admin@city.gov', 'admin123', 'Admin', NULL);
END
GO

-- SEED DATA: Sample Officer and Worker for testing

IF NOT EXISTS (SELECT * FROM employees WHERE email = 'officer@city.gov')
BEGIN
    INSERT INTO employees (name, email, password, role, department_id)
    VALUES ('Jane Officer', 'officer@city.gov', 'officer123', 'Officer', 1);
END
GO

IF NOT EXISTS (SELECT * FROM employees WHERE email = 'worker@city.gov')
BEGIN
    INSERT INTO employees (name, email, password, role, department_id)
    VALUES ('Bob Worker', 'worker@city.gov', 'worker123', 'Worker', 1);
END
GO

-- SEED DATA: Sample Citizen
-- Email: citizen@gmail.com | Password: citizen123

IF NOT EXISTS (SELECT * FROM citizens WHERE email = 'citizen@gmail.com')
BEGIN
    INSERT INTO citizens (name, email, password)
    VALUES ('Alice Citizen', 'citizen@gmail.com', 'citizen123');
END 
GO

PRINT 'SmartCityDB schema and seed data created successfully!';
GO

