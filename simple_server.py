#!/usr/bin/env python3
"""
Minimal Payroll MVP Server
"""

import json
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import cookies
import os
from simple_database import query_db, init_db
from payroll_engine import PayrollEngine

class PayrollHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.payroll = PayrollEngine()
        super().__init__(*args, **kwargs)

    def get_session_employee(self):
        """Get current logged in employee"""
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None

        cookie = cookies.SimpleCookie()
        cookie.load(cookie_header)

        if 'session_id' not in cookie:
            return None

        session_id = cookie['session_id'].value
        session = query_db(
            'SELECT * FROM sessions WHERE session_id = ?',
            (session_id,),
            one=True
        )

        if not session:
            return None

        employee = query_db(
            'SELECT * FROM employees WHERE id = ?',
            (session['employee_id'],),
            one=True
        )

        return dict(employee) if employee else None

    def do_GET(self):
        if self.path.startswith('/static/'):
            self.serve_static()
        elif self.path.startswith('/api/'):
            self.handle_api_get()
        else:
            self.serve_page()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404)

    def serve_static(self):
        file_path = self.path[1:]
        if os.path.exists(file_path):
            content_type = 'text/css' if file_path.endswith('.css') else 'application/javascript'
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def serve_page(self):
        employee = self.get_session_employee()

        if self.path in ['/', '/login']:
            if employee:
                self.redirect('/dashboard')
                return
            template = 'simple_templates/login.html'
        else:
            if not employee:
                self.redirect('/login')
                return

            if self.path == '/dashboard':
                template = 'simple_templates/admin.html' if employee['role'] == 'admin' else 'simple_templates/employee.html'
            else:
                self.send_error(404)
                return

        if os.path.exists(template):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(template, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def handle_api_get(self):
        try:
            employee = self.get_session_employee()

            if self.path == '/api/employees':
                if not employee or employee['role'] != 'admin':
                    self.send_json({'error': 'Unauthorized'}, 403)
                    return

                employees = query_db("SELECT id, name, email, monthly_salary, created_at FROM employees WHERE role = 'employee'")
                self.send_json({'employees': [dict(e) for e in employees]})

            elif self.path == '/api/payslips':
                if not employee:
                    self.send_json({'error': 'Unauthorized'}, 401)
                    return

                if employee['role'] == 'admin':
                    payslips = self.payroll.get_all_payslips()
                else:
                    payslips = self.payroll.get_employee_payslips(employee['id'])

                self.send_json({'payslips': payslips})

            elif self.path == '/api/me':
                if employee:
                    self.send_json({
                        'id': employee['id'],
                        'name': employee['name'],
                        'email': employee['email'],
                        'role': employee['role']
                    })
                else:
                    self.send_json({'error': 'Not authenticated'}, 401)

            else:
                self.send_error(404)

        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_api_post(self):
        try:
            content_length = self.headers.get('Content-Length')
            data = {}
            if content_length:
                post_data = self.rfile.read(int(content_length))
                data = json.loads(post_data.decode('utf-8'))

            if self.path == '/api/login':
                email = data.get('email')
                password = data.get('password')
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                emp = query_db(
                    'SELECT * FROM employees WHERE email = ? AND password_hash = ?',
                    (email, password_hash),
                    one=True
                )

                if not emp:
                    self.send_json({'error': 'Invalid credentials'}, 401)
                    return

                session_id = secrets.token_urlsafe(32)
                query_db(
                    'INSERT INTO sessions (session_id, employee_id) VALUES (?, ?)',
                    (session_id, emp['id'])
                )

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Set-Cookie', f"session_id={session_id}; Path=/; HttpOnly; Max-Age=86400")
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'role': emp['role']
                }).encode())

            elif self.path == '/api/logout':
                cookie_header = self.headers.get('Cookie')
                if cookie_header:
                    cookie = cookies.SimpleCookie()
                    cookie.load(cookie_header)
                    if 'session_id' in cookie:
                        session_id = cookie['session_id'].value
                        query_db('DELETE FROM sessions WHERE session_id = ?', (session_id,))

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Set-Cookie', 'session_id=; Path=/; HttpOnly; Max-Age=0')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())

            elif self.path == '/api/employees':
                employee = self.get_session_employee()
                if not employee or employee['role'] != 'admin':
                    self.send_json({'error': 'Unauthorized'}, 403)
                    return

                name = data.get('name')
                email = data.get('email')
                salary = float(data.get('monthly_salary'))
                password = data.get('password', 'password123')
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                emp_id = query_db(
                    'INSERT INTO employees (name, email, monthly_salary, password_hash) VALUES (?, ?, ?, ?)',
                    (name, email, salary, password_hash)
                )

                self.send_json({'success': True, 'employee_id': emp_id})

            elif self.path == '/api/payroll/run':
                employee = self.get_session_employee()
                if not employee or employee['role'] != 'admin':
                    self.send_json({'error': 'Unauthorized'}, 403)
                    return

                month = data.get('month')
                year = int(data.get('year'))

                generated = self.payroll.run_monthly_payroll(month, year)
                self.send_json({
                    'success': True,
                    'generated': len(generated),
                    'payslips': generated
                })

            else:
                self.send_error(404)

        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

def run_server(port=8080):
    server = HTTPServer(('', port), PayrollHandler)
    print(f"\nPayroll MVP Server running on http://localhost:{port}")
    print("Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

if __name__ == '__main__':
    init_db()
    run_server()
