"""
Payroll Service Module
Handles payroll processing, calculations, and payslip generation
"""

from modules.database import execute_query
from datetime import datetime, timedelta
import calendar

class PayrollService:
    def __init__(self):
        self.tax_rate = 0.20  # 20% tax rate (configurable)
        self.social_security_rate = 0.062  # 6.2%
        self.medicare_rate = 0.0145  # 1.45%

    def calculate_gross_pay(self, base_salary, bonuses=0):
        """Calculate gross pay"""
        return base_salary + bonuses

    def calculate_tax_deductions(self, gross_pay):
        """Calculate tax deductions"""
        federal_tax = gross_pay * self.tax_rate
        social_security = gross_pay * self.social_security_rate
        medicare = gross_pay * self.medicare_rate
        
        return {
            'federal_tax': federal_tax,
            'social_security': social_security,
            'medicare': medicare,
            'total': federal_tax + social_security + medicare
        }

    def calculate_net_pay(self, gross_pay, tax_deductions, other_deductions=0):
        """Calculate net pay after all deductions"""
        return gross_pay - tax_deductions - other_deductions

    def process_payroll(self, payroll_data):
        """Process payroll for employees"""
        try:
            employee_id = payroll_data['employee_id']
            pay_period_start = payroll_data['pay_period_start']
            pay_period_end = payroll_data['pay_period_end']
            base_salary = float(payroll_data['base_salary'])
            bonuses = float(payroll_data.get('bonuses', 0))
            other_deductions = float(payroll_data.get('deductions', 0))
            
            # Calculate payroll
            gross_pay = self.calculate_gross_pay(base_salary, bonuses)
            tax_breakdown = self.calculate_tax_deductions(gross_pay)
            net_pay = self.calculate_net_pay(gross_pay, tax_breakdown['total'], other_deductions)
            
            # Save to database
            query = '''
                INSERT INTO payroll 
                (employee_id, pay_period_start, pay_period_end, base_salary, 
                 bonuses, deductions, gross_pay, tax_deductions, net_pay)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
                employee_id, pay_period_start, pay_period_end, base_salary,
                bonuses, other_deductions, gross_pay, tax_breakdown['total'], net_pay
            )
            
            execute_query(query, params)
            
            return {
                'success': True,
                'message': 'Payroll processed successfully',
                'payroll_details': {
                    'employee_id': employee_id,
                    'gross_pay': gross_pay,
                    'tax_breakdown': tax_breakdown,
                    'other_deductions': other_deductions,
                    'net_pay': net_pay
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing payroll: {str(e)}'
            }

    def approve_payroll(self, payroll_id, approved_by_user_id=None):
        """Approve a pending payroll record.

        This transitions status from 'pending' -> 'approved'.
        """
        try:
            query = """
                UPDATE payroll
                SET status = 'approved'
                WHERE id = ? AND status = 'pending'
            """
            rows = execute_query(query, (payroll_id,))

            # In this project, execute_query returns an int for UPDATE/DELETE (rows affected).
            affected = rows if isinstance(rows, int) else (1 if rows is not None else 0)

            if affected > 0:
                return {'success': True, 'message': 'Payroll approved'}
            return {'success': False, 'message': 'Payroll not found or not pending'}
        except Exception as e:
            return {'success': False, 'message': f'Error approving payroll: {str(e)}'}

    def get_payroll_for_employee(self, employee_id):
        """Get payroll records for a single employee (all history)."""
        try:
            query = '''
                SELECT
                    p.*,
                    COALESCE(e.first_name, 'Deleted') AS first_name,
                    COALESCE(e.last_name, 'Employee') AS last_name,
                    e.position
                FROM payroll p
                LEFT JOIN employees e ON p.employee_id = e.employee_id
                WHERE p.employee_id = ?
                ORDER BY p.created_at DESC
            '''
            records = execute_query(query, (employee_id,))

            total_gross = sum(record['gross_pay'] for record in records)
            total_net = sum(record['net_pay'] for record in records)
            total_taxes = sum(record['tax_deductions'] for record in records)

            return {
                'success': True,
                'summary': {
                    'total_payslips': len(records),
                    'total_gross_pay': total_gross,
                    'total_net_pay': total_net,
                    'total_tax_deductions': total_taxes
                },
                'records': records
            }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching employee payroll: {str(e)}'}

    def get_payroll_summary(self):
        """Get payroll summary for current month.

        The dashboard and payroll pages are meant to show *recently processed* payrolls.
        Filtering by pay-period boundaries can hide valid records (e.g., overlapping periods).
        So we filter by payroll.created_at for the current month.

        We also use a LEFT JOIN so payroll records still appear even if an employee record
        was permanently deleted.
        """
        try:
            # Current month's date window (server local time)
            current_date = datetime.now()
            first_day = current_date.replace(day=1)
            last_day = current_date.replace(
                day=calendar.monthrange(current_date.year, current_date.month)[1]
            )
            
            query = '''
                SELECT
                    p.*,
                    COALESCE(e.first_name, 'Deleted') AS first_name,
                    COALESCE(e.last_name, 'Employee') AS last_name,
                    e.position
                FROM payroll p
                LEFT JOIN employees e ON p.employee_id = e.employee_id
                WHERE DATE(p.created_at) >= ? AND DATE(p.created_at) <= ?
                ORDER BY p.created_at DESC
            '''

            payroll_records = execute_query(
                query,
                (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d'))
            )
            
            # Calculate totals
            total_gross = sum(record['gross_pay'] for record in payroll_records)
            total_net = sum(record['net_pay'] for record in payroll_records)
            total_taxes = sum(record['tax_deductions'] for record in payroll_records)
            
            return {
                'success': True,
                'summary': {
                    'total_employees': len(payroll_records),
                    'total_gross_pay': total_gross,
                    'total_net_pay': total_net,
                    'total_tax_deductions': total_taxes
                },
                'records': payroll_records
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching payroll summary: {str(e)}'
            }

    def generate_payslip(self, employee_id, payroll_id):
        """Generate payslip for specific employee and payroll period"""
        try:
            query = '''
                SELECT
                    p.*,
                    COALESCE(e.first_name, 'Deleted') AS first_name,
                    COALESCE(e.last_name, 'Employee') AS last_name,
                    e.position,
                    e.department
                FROM payroll p
                LEFT JOIN employees e ON p.employee_id = e.employee_id
                WHERE p.id = ? AND p.employee_id = ?
            '''
            
            records = execute_query(query, (payroll_id, employee_id))
            
            if records:
                return {
                    'success': True,
                    'payslip': records[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Payslip not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating payslip: {str(e)}'
            }