"""
Minimal Database Setup for Payroll MVP
"""

import sqlite3
import hashlib

DATABASE_PATH = 'payroll_mvp.db'

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize minimal database schema"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            monthly_salary REAL NOT NULL,
            role TEXT DEFAULT 'employee',
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payslips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            year INTEGER NOT NULL,
            gross_pay REAL NOT NULL,
            deductions REAL NOT NULL,
            net_pay REAL NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            UNIQUE(employee_id, month, year)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            employee_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')

    admin_email = 'admin@payroll.com'
    cursor.execute('SELECT * FROM employees WHERE email = ?', (admin_email,))
    if not cursor.fetchone():
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO employees (name, email, monthly_salary, role, password_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', admin_email, 0, 'admin', password_hash))
        print(f"\n{'='*50}")
        print("ADMIN ACCOUNT CREATED")
        print(f"{'='*50}")
        print(f"Email: {admin_email}")
        print("Password: admin123")
        print(f"{'='*50}\n")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def query_db(query, args=(), one=False):
    """Execute query and return results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, args)

    if query.strip().upper().startswith('SELECT'):
        results = cursor.fetchall()
        conn.close()
        return (results[0] if results else None) if one else results
    else:
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
