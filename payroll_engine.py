"""
Core Payroll Calculation Engine
Simple deduction model: 20% tax + 5% insurance
"""

from simple_database import query_db
from datetime import datetime

class PayrollEngine:
    TAX_RATE = 0.20
    INSURANCE_RATE = 0.05

    def calculate_payslip(self, gross_pay):
        """Calculate net pay from gross"""
        deductions = gross_pay * (self.TAX_RATE + self.INSURANCE_RATE)
        net_pay = gross_pay - deductions
        return {
            'gross_pay': round(gross_pay, 2),
            'deductions': round(deductions, 2),
            'net_pay': round(net_pay, 2)
        }

    def run_monthly_payroll(self, month, year):
        """Generate payslips for all employees for given month/year"""
        employees = query_db(
            "SELECT * FROM employees WHERE role = 'employee'",
            ()
        )

        generated = []
        for emp in employees:
            existing = query_db(
                "SELECT * FROM payslips WHERE employee_id = ? AND month = ? AND year = ?",
                (emp['id'], month, year),
                one=True
            )

            if existing:
                continue

            calc = self.calculate_payslip(emp['monthly_salary'])

            query_db('''
                INSERT INTO payslips (employee_id, month, year, gross_pay, deductions, net_pay)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (emp['id'], month, year, calc['gross_pay'], calc['deductions'], calc['net_pay']))

            generated.append({
                'employee_id': emp['id'],
                'employee_name': emp['name'],
                'month': month,
                'year': year,
                **calc
            })

        return generated

    def get_employee_payslips(self, employee_id):
        """Get all payslips for an employee"""
        payslips = query_db('''
            SELECT p.*, e.name as employee_name
            FROM payslips p
            JOIN employees e ON p.employee_id = e.id
            WHERE p.employee_id = ?
            ORDER BY p.year DESC, p.month DESC
        ''', (employee_id,))

        return [dict(p) for p in payslips]

    def get_all_payslips(self):
        """Get all payslips (admin view)"""
        payslips = query_db('''
            SELECT p.*, e.name as employee_name, e.email
            FROM payslips p
            JOIN employees e ON p.employee_id = e.id
            ORDER BY p.year DESC, p.month DESC, e.name
        ''', ())

        return [dict(p) for p in payslips]
