"""
Database module for TeamRoll
Handles SQLite database initialization and connections
"""

import sqlite3
import os

DATABASE_PATH = 'teamroll.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            position TEXT NOT NULL,
            department TEXT,
            hire_date DATE NOT NULL,
            base_salary REAL NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create payroll table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            pay_period_start DATE NOT NULL,
            pay_period_end DATE NOT NULL,
            base_salary REAL NOT NULL,
            bonuses REAL DEFAULT 0,
            deductions REAL DEFAULT 0,
            gross_pay REAL NOT NULL,
            tax_deductions REAL NOT NULL,
            net_pay REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date DATE NOT NULL,
            check_in TIME,
            check_out TIME,
            hours_worked REAL DEFAULT 0,
            leave_type TEXT,
            status TEXT DEFAULT 'present',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def execute_query(query, params=None):
    """Execute a query and return results"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    if query.strip().upper().startswith('SELECT'):
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    else:
        conn.commit()
        conn.close()
        return cursor.rowcount