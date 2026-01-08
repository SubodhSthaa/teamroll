"""
Authentication Service Module
Handles user authentication, registration, and session management
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from modules.database import execute_query

class AuthService:
    def __init__(self):
        self.session_duration_hours = 24

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_session_id(self):
        """Generate a secure session ID"""
        return secrets.token_urlsafe(32)

    def register_user(self, user_data):
        """Register a new user"""
        try:
            username = user_data['username']
            password = user_data['password']
            email = user_data['email']
            role = user_data.get('role', 'employee')
            employee_id = user_data.get('employee_id')

            if role not in ['admin', 'employee']:
                return {
                    'success': False,
                    'message': 'Invalid role. Must be admin or employee.'
                }

            existing_user = execute_query(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            )

            if existing_user:
                return {
                    'success': False,
                    'message': 'Username already exists'
                }

            pending_user = execute_query(
                'SELECT * FROM pending_registrations WHERE username = ? AND status = "pending"',
                (username,)
            )

            if pending_user:
                return {
                    'success': False,
                    'message': 'Username already has a pending registration request'
                }

            existing_email = execute_query(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            )

            if existing_email:
                return {
                    'success': False,
                    'message': 'Email already registered'
                }

            pending_email = execute_query(
                'SELECT * FROM pending_registrations WHERE email = ? AND status = "pending"',
                (email,)
            )

            if pending_email:
                return {
                    'success': False,
                    'message': 'Email already has a pending registration request'
                }

            password_hash = self.hash_password(password)

            if role == 'admin':
                query = '''
                    INSERT INTO users (username, password_hash, role, email)
                    VALUES (?, ?, 'admin', ?)
                '''
                execute_query(query, (username, password_hash, email))

                return {
                    'success': True,
                    'message': 'Admin account created successfully'
                }

            if role == 'employee':
                if not employee_id:
                    return {
                        'success': False,
                        'message': 'Employee ID is required for employee registration'
                    }

                employee = execute_query(
                    'SELECT * FROM employees WHERE employee_id = ?',
                    (employee_id,)
                )
                if not employee:
                    return {
                        'success': False,
                        'message': 'Invalid employee ID. Please contact your administrator.'
                    }

                existing_emp_user = execute_query(
                    'SELECT * FROM users WHERE employee_id = ?',
                    (employee_id,)
                )
                if existing_emp_user:
                    return {
                        'success': False,
                        'message': 'This employee ID already has an account'
                    }

                query = '''
                    INSERT INTO pending_registrations (username, password_hash, email, employee_id, status)
                    VALUES (?, ?, ?, ?, 'pending')
                '''
                execute_query(query, (username, password_hash, email, employee_id))

                return {
                    'success': True,
                    'message': 'Registration request submitted. Please wait for admin approval.',
                    'requires_approval': True
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error registering user: {str(e)}'
            }

    def login(self, username, password):
        """Authenticate user and create session"""
        try:
            password_hash = self.hash_password(password)

            query = '''
                SELECT u.*, e.first_name, e.last_name
                FROM users u
                LEFT JOIN employees e ON u.employee_id = e.employee_id
                WHERE u.username = ? AND u.password_hash = ? AND u.is_active = 1
            '''
            users = execute_query(query, (username, password_hash))

            if not users:
                return {
                    'success': False,
                    'message': 'Invalid username or password'
                }

            user = users[0]

            session_id = self.generate_session_id()
            expires_at = datetime.now() + timedelta(hours=self.session_duration_hours)

            query = '''
                INSERT INTO sessions (session_id, user_id, expires_at)
                VALUES (?, ?, ?)
            '''
            execute_query(query, (session_id, user['id'], expires_at.strftime('%Y-%m-%d %H:%M:%S')))

            return {
                'success': True,
                'message': 'Login successful',
                'session_id': session_id,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role'],
                    'employee_id': user['employee_id'],
                    'email': user['email'],
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name')
                }
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error during login: {str(e)}'
            }

    def verify_session(self, session_id):
        """Verify if session is valid"""
        try:
            if not session_id:
                return None

            query = '''
                SELECT s.*, u.username, u.role, u.employee_id, u.email,
                       e.first_name, e.last_name
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                LEFT JOIN employees e ON u.employee_id = e.employee_id
                WHERE s.session_id = ? AND s.expires_at > datetime('now') AND u.is_active = 1
            '''
            sessions = execute_query(query, (session_id,))

            if sessions:
                return sessions[0]
            return None

        except Exception as e:
            print(f"Error verifying session: {e}")
            return None

    def logout(self, session_id):
        """Delete session (logout)"""
        try:
            if not session_id:
                return {
                    'success': True,
                    'message': 'No active session'
                }

            query = 'DELETE FROM sessions WHERE session_id = ?'
            rows_deleted = execute_query(query, (session_id,))

            return {
                'success': True,
                'message': 'Logged out successfully'
            }

        except Exception as e:
            print(f"Logout error: {str(e)}")
            return {
                'success': True,
                'message': 'Logged out'
            }

    def get_pending_registrations(self):
        """Get all pending registration requests"""
        try:
            query = '''
                SELECT pr.*, e.first_name, e.last_name, e.position, e.department
                FROM pending_registrations pr
                JOIN employees e ON pr.employee_id = e.employee_id
                WHERE pr.status = 'pending'
                ORDER BY pr.created_at DESC
            '''
            return execute_query(query)
        except Exception as e:
            print(f"Error getting pending registrations: {e}")
            return []

    def approve_registration(self, registration_id, admin_user_id, notes=''):
        """Approve a pending registration"""
        try:
            pending = execute_query(
                'SELECT * FROM pending_registrations WHERE id = ? AND status = "pending"',
                (registration_id,)
            )

            if not pending:
                return {
                    'success': False,
                    'message': 'Registration request not found or already processed'
                }

            reg = pending[0]

            query = '''
                INSERT INTO users (username, password_hash, role, employee_id, email)
                VALUES (?, ?, 'employee', ?, ?)
            '''
            execute_query(query, (reg['username'], reg['password_hash'], reg['employee_id'], reg['email']))

            update_query = '''
                UPDATE pending_registrations
                SET status = 'approved', reviewed_at = datetime('now'), reviewed_by = ?, admin_notes = ?
                WHERE id = ?
            '''
            execute_query(update_query, (admin_user_id, notes, registration_id))

            return {
                'success': True,
                'message': 'Registration approved successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error approving registration: {str(e)}'
            }

    def reject_registration(self, registration_id, admin_user_id, notes=''):
        """Reject a pending registration"""
        try:
            pending = execute_query(
                'SELECT * FROM pending_registrations WHERE id = ? AND status = "pending"',
                (registration_id,)
            )

            if not pending:
                return {
                    'success': False,
                    'message': 'Registration request not found or already processed'
                }

            update_query = '''
                UPDATE pending_registrations
                SET status = 'rejected', reviewed_at = datetime('now'), reviewed_by = ?, admin_notes = ?
                WHERE id = ?
            '''
            execute_query(update_query, (admin_user_id, notes, registration_id))

            return {
                'success': True,
                'message': 'Registration rejected'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error rejecting registration: {str(e)}'
            }

    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        try:
            query = "DELETE FROM sessions WHERE expires_at < datetime('now')"
            execute_query(query)
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
