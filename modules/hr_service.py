"""
HR Service Module
Handles employee management, profiles, and HR-related operations
"""

from modules.database import execute_query
from datetime import datetime
import uuid

class HRService:
    def __init__(self):
        pass

    def add_employee(self, employee_data):
        """Add a new employee to the system"""
        try:
            # Generate unique employee ID
            employee_id = f"EMP{str(uuid.uuid4())[:8].upper()}"
            
            query = '''
                INSERT INTO employees 
                (employee_id, first_name, last_name, email, phone, position, 
                 department, hire_date, base_salary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                employee_id,
                employee_data['first_name'],
                employee_data['last_name'],
                employee_data['email'],
                employee_data.get('phone', ''),
                employee_data['position'],
                employee_data.get('department', ''),
                employee_data['hire_date'],
                employee_data['base_salary']
            )
            
            execute_query(query, params)
            
            return {
                'success': True,
                'message': 'Employee added successfully',
                'employee_id': employee_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding employee: {str(e)}'
            }

    def get_all_employees(self, include_inactive: bool = False):
        """Get employees.

        Default behavior is to return only active employees so deactivated
        ("deleted") employees no longer appear in the UI.

        Set include_inactive=True when you explicitly want both active and
        inactive employees.
        """
        try:
            if include_inactive:
                query = '''
                    SELECT * FROM employees
                    ORDER BY
                        CASE WHEN status = 'active' THEN 0 ELSE 1 END,
                        last_name,
                        first_name
                '''
                employees = execute_query(query)
            else:
                query = '''
                    SELECT * FROM employees
                    WHERE status = 'active'
                    ORDER BY last_name, first_name
                '''
                employees = execute_query(query)
            
            return {
                'success': True,
                'employees': employees
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching employees: {str(e)}'
            }

    def get_employee(self, employee_id):
        """Get specific employee by ID"""
        try:
            query = 'SELECT * FROM employees WHERE employee_id = ?'
            employees = execute_query(query, (employee_id,))
            
            if employees:
                return {
                    'success': True,
                    'employee': employees[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Employee not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching employee: {str(e)}'
            }

    def update_employee(self, employee_id, employee_data):
        """Update employee information"""
        try:
            query = '''
                UPDATE employees 
                SET first_name = ?, last_name = ?, email = ?, phone = ?,
                    position = ?, department = ?, base_salary = ?
                WHERE employee_id = ?
            '''
            
            params = (
                employee_data['first_name'],
                employee_data['last_name'],
                employee_data['email'],
                employee_data.get('phone', ''),
                employee_data['position'],
                employee_data.get('department', ''),
                employee_data['base_salary'],
                employee_id
            )
            
            rows_affected = execute_query(query, params)
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'Employee updated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Employee not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating employee: {str(e)}'
            }

    def deactivate_employee(self, employee_id):
        """Deactivate an employee (soft delete)"""
        try:
            query = 'UPDATE employees SET status = ? WHERE employee_id = ?'
            rows_affected = execute_query(query, ('inactive', employee_id))
            
            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'Employee deactivated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Employee not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deactivating employee: {str(e)}'
            }

    def delete_employee(self, employee_id):
        """Permanently delete an employee (hard delete).

        This removes the employee row and also deletes dependent rows in
        payroll, attendance, users, and pending_registrations that reference
        the employee_id to avoid orphaned data.
        """
        try:
            # Delete dependent records first
            execute_query('DELETE FROM payroll WHERE employee_id = ?', (employee_id,))
            execute_query('DELETE FROM attendance WHERE employee_id = ?', (employee_id,))
            execute_query('DELETE FROM users WHERE employee_id = ?', (employee_id,))
            execute_query('DELETE FROM pending_registrations WHERE employee_id = ?', (employee_id,))

            # Delete the employee record
            rows_affected = execute_query('DELETE FROM employees WHERE employee_id = ?', (employee_id,))

            if rows_affected > 0:
                return {
                    'success': True,
                    'message': 'Employee deleted permanently'
                }
            else:
                return {
                    'success': False,
                    'message': 'Employee not found'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting employee: {str(e)}'
            }
