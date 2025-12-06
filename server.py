#!/usr/bin/env python3
"""
TeamRoll Server - Main application server
Handles HTTP requests and routes them to appropriate modules
"""

import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
from modules.hr_service import HRService
from modules.payroll_service import PayrollService
from modules.accounting_service import AccountingService


class TeamRollHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.hr_service = HRService()
        self.payroll_service = PayrollService()
        self.accounting_service = AccountingService()
        super().__init__(*args, **kwargs)

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
        path = parsed_path.path

        if path.startswith('/api/'):
            self.handle_api_post(path)
        else:
            self.send_error(404)

    def serve_static_file(self, path):
        file_path = path[1:]

        if os.path.exists(file_path):
            content_type = 'text/css' if path.endswith('.css') else 'text/plain'

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()

            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def serve_template(self, path):
        if path == '/' or path == '/index.html':
            template_path = 'templates/index.html'
        elif path == '/dashboard':
            template_path = 'templates/dashboard.html'
        elif path == '/employees':
            template_path = 'templates/employees.html'
        elif path == '/payroll':
            template_path = 'templates/payroll.html'
        else:
            self.send_error(404)
            return

        if os.path.exists(template_path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            with open(template_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def handle_api_get(self, path):
        try:
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
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_api_post(self, path):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if path == '/api/employees':
                result = self.hr_service.add_employee(data)
                self.send_json_response(result)
            elif path == '/api/payroll/process':
                result = self.payroll_service.process_payroll(data)
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
