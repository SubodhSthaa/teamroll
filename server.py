#!/usr/bin/env python3
"""
TeamRoll Server - Main application server
Handles HTTP requests and routes them to appropriate modules
"""

import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from http import cookies
import os
from modules.hr_service import HRService
from modules.payroll_service import PayrollService
from modules.accounting_service import AccountingService
from modules.attendance_service import AttendanceService
from modules.auth_service import AuthService


class TeamRollHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.hr_service = HRService()
        self.payroll_service = PayrollService()
        self.accounting_service = AccountingService()
        self.attendance_service = AttendanceService()
        self.auth_service = AuthService()
        super().__init__(*args, **kwargs)

    def get_session_id(self):
        """Extract session ID from cookies"""
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = cookies.SimpleCookie()
            cookie.load(cookie_header)
            if 'session_id' in cookie:
                return cookie['session_id'].value
        return None

    def get_current_user(self):
        """Get current authenticated user"""
        session_id = self.get_session_id()
        if session_id:
            return self.auth_service.verify_session(session_id)
        return None

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/static/'):
            self.serve_static_file(path)
        elif path.startswith('/api/'):
            self.handle_api_get(path)
        else:
            self.serve_template(path)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path= parsed_path.path

        if path.startswith('/api/'):
            self.handle_api_post(path)
            return
        self.send_error(404)

    def do_PUT(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/'):
            self.handle_api_put(path)
            return
        self.send_error(404)

    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/api/'):
            self.handle_api_delete(path)
            return
        self.send_error(404)


    def serve_static_file(self, path):
        file_path = path[1:]

        if os.path.exists(file_path):
            if path.endswith('.css'):
                content_type = 'text/css'
            elif path.endswith('.js'):
                content_type = 'application/javascript'
            else:
                content_type = 'text/plain'

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def serve_template(self, path):
        public_pages = ['/', '/index.html', '/login', '/register']
        is_public = path in public_pages

        if is_public:
            if path == '/' or path == '/index.html':
                template_path = 'templates/index.html'
            elif path == '/login':
                template_path = 'templates/login.html'
            elif path == '/register':
                template_path = 'templates/register.html'
        else:
            user = self.get_current_user()
            if not user:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.end_headers()
                return

            if path == '/dashboard':
                if user['role'] == 'admin':
                    template_path = 'templates/admin_dashboard.html'
                else:
                    template_path = 'templates/employee_dashboard.html'
            elif path == '/employees':
                if user['role'] == 'admin':
                    template_path = 'templates/employees.html'
                else:
                    self.send_error(403)
                    return
            elif path == '/payroll':
                if user['role'] == 'admin':
                    template_path = 'templates/payroll.html'
                else:
                    template_path = 'templates/employee_payroll.html'
            elif path == '/attendance':
                template_path = 'templates/attendance.html'
            elif path == '/admin/registrations':
                if user['role'] == 'admin':
                    template_path = 'templates/admin_registrations.html'
                else:
                    self.send_error(403)
                    return
            else:
                self.send_error(404)
                return

        if os.path.exists(template_path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')

            if not is_public:
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')

            self.end_headers()

            with open(template_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def handle_api_get(self, path):
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            if path == '/api/employees':
                employees = self.hr_service.get_all_employees()
                self.send_json_response(employees)
            elif path.startswith('/api/employees/'):
                emp_id = path.split('/')[-1]
                employee = self.hr_service.get_employee(emp_id)
                self.send_json_response(employee)
            elif path == '/api/payroll':
                payroll_data = self.payroll_service.get_payroll_summary()
                self.send_json_response(payroll_data)
            elif path == '/api/attendance':
                date = query_params.get('date', [None])[0]
                attendance_data = self.attendance_service.get_all_attendance(date)
                self.send_json_response(attendance_data)
            elif path.startswith('/api/attendance/employee/'):
                emp_id = path.split('/')[-1]
                start_date = query_params.get('start_date', [None])[0]
                end_date = query_params.get('end_date', [None])[0]
                attendance_data = self.attendance_service.get_attendance_by_employee(emp_id, start_date, end_date)
                self.send_json_response(attendance_data)
            elif path.startswith('/api/attendance/status/'):
                emp_id = path.split('/')[-1]
                status = self.attendance_service.get_today_status(emp_id)
                self.send_json_response(status)
            elif path == '/api/auth/me':
                user = self.get_current_user()
                if user:
                    self.send_json_response({
                        'success': True,
                        'user': {
                            'username': user['username'],
                            'role': user['role'],
                            'employee_id': user['employee_id'],
                            'email': user['email'],
                            'first_name': user.get('first_name'),
                            'last_name': user.get('last_name')
                        }
                    })
                else:
                    self.send_json_response({'success': False, 'message': 'Not authenticated'}, 401)
            elif path == '/api/admin/pending-registrations':
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return
                pending = self.auth_service.get_pending_registrations()
                self.send_json_response({'success': True, 'registrations': pending})
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_api_post(self, path):
        try:
            content_length = self.headers.get('Content-Length')
            if content_length:
                post_data = self.rfile.read(int(content_length))
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}

            if path == '/api/employees':
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return

                result = self.hr_service.add_employee(data)
                self.send_json_response(result)
            elif path == '/api/payroll/process':
                result = self.payroll_service.process_payroll(data)
                self.send_json_response(result)
            elif path == '/api/attendance/checkin':
                result = self.attendance_service.check_in(data['employee_id'])
                self.send_json_response(result)
            elif path == '/api/attendance/checkout':
                result = self.attendance_service.check_out(data['employee_id'])
                self.send_json_response(result)
            elif path == '/api/attendance/leave':
                result = self.attendance_service.mark_leave(data)
                self.send_json_response(result)
            elif path == '/api/auth/register':
                result = self.auth_service.register_user(data)
                self.send_json_response(result)
            elif path == '/api/auth/login':
                result = self.auth_service.login(data.get('username'), data.get('password'))
                if result['success']:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Set-Cookie', f"session_id={result['session_id']}; Path=/; HttpOnly; Max-Age=86400")
                    self.end_headers()
                    response = json.dumps(result, indent=2)
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_json_response(result, 401)
                return
            elif path == '/api/auth/logout':
                session_id = self.get_session_id()
                result = self.auth_service.logout(session_id)
                if result['success']:
                    self.send_response(302)
                    self.send_header(
                             'Set-Cookie',
                            'session_id=; Path=/; HttpOnly; expires=Thu, 01 Jan 1970 00:00:00 GMT'
                            )
                    self.send_header('Location', '/login')
                    self.end_headers()
                else:
                    self.send_json_response(result, 400)
                return
            elif path == '/api/admin/approve-registration':
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return
                result = self.auth_service.approve_registration(
                    data['registration_id'],
                    user['id'],
                    data.get('notes', '')
                )
                self.send_json_response(result)
            elif path == '/api/admin/reject-registration':
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return
                result = self.auth_service.reject_registration(
                    data['registration_id'],
                    user['id'],
                    data.get('notes', '')
                )
                self.send_json_response(result)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_api_put(self, path):
        try:
            content_length = self.headers.get('Content-Length')
            if content_length:
                put_data = self.rfile.read(int(content_length))
                data = json.loads(put_data.decode('utf-8'))
            else:
                data = {}

            if path.startswith('/api/employees/'):
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return

                emp_id = path.split('/')[-1]
                result = self.hr_service.update_employee(emp_id, data)
                self.send_json_response(result)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_api_delete(self, path):
        try:
            if path.startswith('/api/employees/'):
                user = self.get_current_user()
                if not user or user['role'] != 'admin':
                    self.send_json_response({'success': False, 'message': 'Admin access required'}, 403)
                    return

                emp_id = path.split('/')[-1]
                result = self.hr_service.deactivate_employee(emp_id)
                self.send_json_response(result)
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def self_render_template(self, template_path, context):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")



def run_server(port=8080):
    """Start the TeamRoll server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TeamRollHandler)

    print(f"TeamRoll server running on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == '__main__':
    from modules.database import init_database
    init_database()

    run_server()
