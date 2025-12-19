"""
Attendance Service Module
Handles employee attendance tracking, check-in/check-out, and leave management
"""

from modules.database import execute_query
from datetime import datetime, timedelta, time
import calendar

class AttendanceService:
    def __init__(self):
        self.standard_hours = 8  # Standard work hours per day
        self.grace_period_minutes = 15  # Grace period for late check-in

    def check_in(self, employee_id):
        """Record employee check-in"""
        try:
            today = datetime.now().date()
            current_time = datetime.now().time()

            # Check if already checked in today
            query = '''
                SELECT * FROM attendance
                WHERE employee_id = ? AND date = ? AND check_in IS NOT NULL
            '''
            existing = execute_query(query, (employee_id, today.strftime('%Y-%m-%d')))

            if existing:
                return {
                    'success': False,
                    'message': 'Already checked in today'
                }

            # Create new attendance record
            query = '''
                INSERT INTO attendance (employee_id, date, check_in, status)
                VALUES (?, ?, ?, ?)
            '''
            execute_query(query, (employee_id, today.strftime('%Y-%m-%d'),
                                 current_time.strftime('%H:%M:%S'), 'present'))

            return {
                'success': True,
                'message': 'Checked in successfully',
                'check_in_time': current_time.strftime('%H:%M:%S')
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking in: {str(e)}'
            }

    def check_out(self, employee_id):
        """Record employee check-out"""
        try:
            today = datetime.now().date()
            current_time = datetime.now().time()

            # Find today's attendance record
            query = '''
                SELECT * FROM attendance
                WHERE employee_id = ? AND date = ? AND check_out IS NULL
            '''
            records = execute_query(query, (employee_id, today.strftime('%Y-%m-%d')))

            if not records:
                return {
                    'success': False,
                    'message': 'No active check-in found for today'
                }

            record = records[0]
            check_in_time = datetime.strptime(record['check_in'], '%H:%M:%S').time()

            # Calculate hours worked
            check_in_datetime = datetime.combine(today, check_in_time)
            check_out_datetime = datetime.combine(today, current_time)
            hours_worked = (check_out_datetime - check_in_datetime).total_seconds() / 3600

            # Update attendance record
            query = '''
                UPDATE attendance
                SET check_out = ?, hours_worked = ?
                WHERE id = ?
            '''
            execute_query(query, (current_time.strftime('%H:%M:%S'),
                                 hours_worked, record['id']))

            return {
                'success': True,
                'message': 'Checked out successfully',
                'check_out_time': current_time.strftime('%H:%M:%S'),
                'hours_worked': round(hours_worked, 2)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking out: {str(e)}'
            }

    def mark_leave(self, leave_data):
        """Mark employee leave"""
        try:
            query = '''
                INSERT INTO attendance
                (employee_id, date, leave_type, status)
                VALUES (?, ?, ?, ?)
            '''

            params = (
                leave_data['employee_id'],
                leave_data['date'],
                leave_data['leave_type'],
                'leave'
            )

            execute_query(query, params)

            return {
                'success': True,
                'message': 'Leave marked successfully'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error marking leave: {str(e)}'
            }

    def get_attendance_by_employee(self, employee_id, start_date=None, end_date=None):
        """Get attendance records for specific employee"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            query = '''
                SELECT a.*, e.first_name, e.last_name, e.position
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.employee_id = ? AND a.date BETWEEN ? AND ?
                ORDER BY a.date DESC
            '''

            records = execute_query(query, (employee_id, start_date, end_date))

            return {
                'success': True,
                'records': records
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching attendance: {str(e)}'
            }

    def get_all_attendance(self, date=None):
        """Get attendance records for all employees for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')

            query = '''
                SELECT a.*, e.first_name, e.last_name, e.position, e.department
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.date = ?
                ORDER BY e.last_name, e.first_name
            '''

            records = execute_query(query, (date,))

            # Get all employees to show who hasn't checked in
            all_employees_query = '''
                SELECT employee_id, first_name, last_name, position, department
                FROM employees
                WHERE status = 'active'
            '''
            all_employees = execute_query(all_employees_query)

            # Find employees who haven't checked in
            checked_in_ids = [r['employee_id'] for r in records]
            absent_employees = [emp for emp in all_employees if emp['employee_id'] not in checked_in_ids]

            return {
                'success': True,
                'date': date,
                'present_records': records,
                'absent_employees': absent_employees
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching attendance: {str(e)}'
            }

    def get_attendance_summary(self, employee_id, year, month):
        """Get monthly attendance summary for an employee"""
        try:
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, calendar.monthrange(year, month)[1])

            query = '''
                SELECT
                    COUNT(*) as total_days,
                    COUNT(CASE WHEN status = 'present' THEN 1 END) as present_days,
                    COUNT(CASE WHEN status = 'leave' THEN 1 END) as leave_days,
                    SUM(hours_worked) as total_hours
                FROM attendance
                WHERE employee_id = ? AND date BETWEEN ? AND ?
            '''

            results = execute_query(query, (employee_id,
                                          first_day.strftime('%Y-%m-%d'),
                                          last_day.strftime('%Y-%m-%d')))

            if results:
                summary = results[0]
                return {
                    'success': True,
                    'summary': {
                        'total_days': summary['total_days'] or 0,
                        'present_days': summary['present_days'] or 0,
                        'leave_days': summary['leave_days'] or 0,
                        'total_hours': summary['total_hours'] or 0,
                        'average_hours': (summary['total_hours'] / summary['present_days']) if summary['present_days'] else 0
                    }
                }
            else:
                return {
                    'success': True,
                    'summary': {
                        'total_days': 0,
                        'present_days': 0,
                        'leave_days': 0,
                        'total_hours': 0,
                        'average_hours': 0
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating summary: {str(e)}'
            }

    def get_today_status(self, employee_id):
        """Get today's attendance status for an employee"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            query = '''
                SELECT * FROM attendance
                WHERE employee_id = ? AND date = ?
            '''

            records = execute_query(query, (employee_id, today))

            if records:
                record = records[0]
                return {
                    'success': True,
                    'has_checked_in': record['check_in'] is not None,
                    'has_checked_out': record['check_out'] is not None,
                    'status': record['status'],
                    'check_in_time': record['check_in'],
                    'check_out_time': record['check_out'],
                    'hours_worked': record['hours_worked']
                }
            else:
                return {
                    'success': True,
                    'has_checked_in': False,
                    'has_checked_out': False,
                    'status': 'not_checked_in'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching status: {str(e)}'
            }
