"""
Accounting Service Module
Handles financial calculations, tax compliance, and reporting
"""

from modules.database import execute_query
from datetime import datetime, timedelta
import calendar

class AccountingService:
    def __init__(self):
        pass

    def get_monthly_report(self, year, month):
        """Generate monthly financial report"""
        try:
            # Get first and last day of the month
            first_day = datetime(year, month, 1)
            last_day = datetime(year, month, calendar.monthrange(year, month)[1])
            
            query = '''
                SELECT 
                    COUNT(*) as total_employees,
                    SUM(gross_pay) as total_gross_pay,
                    SUM(tax_deductions) as total_tax_deductions,
                    SUM(deductions) as total_other_deductions,
                    SUM(net_pay) as total_net_pay
                FROM payroll 
                WHERE pay_period_start >= ? AND pay_period_end <= ?
            '''
            
            results = execute_query(query, (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))
            
            if results:
                report = results[0]
                return {
                    'success': True,
                    'report': {
                        'period': f"{calendar.month_name[month]} {year}",
                        'total_employees': report['total_employees'] or 0,
                        'total_gross_pay': report['total_gross_pay'] or 0,
                        'total_tax_deductions': report['total_tax_deductions'] or 0,
                        'total_other_deductions': report['total_other_deductions'] or 0,
                        'total_net_pay': report['total_net_pay'] or 0
                    }
                }
            else:
                return {
                    'success': True,
                    'report': {
                        'period': f"{calendar.month_name[month]} {year}",
                        'total_employees': 0,
                        'total_gross_pay': 0,
                        'total_tax_deductions': 0,
                        'total_other_deductions': 0,
                        'total_net_pay': 0
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }

    def get_tax_summary(self, year):
        """Get annual tax summary"""
        try:
            query = '''
                SELECT 
                    SUM(tax_deductions) as total_taxes,
                    COUNT(DISTINCT employee_id) as total_employees,
                    strftime('%m', pay_period_start) as month,
                    SUM(gross_pay) as monthly_gross
                FROM payroll 
                WHERE strftime('%Y', pay_period_start) = ?
                GROUP BY strftime('%m', pay_period_start)
                ORDER BY month
            '''
            
            monthly_data = execute_query(query, (str(year),))
            
            # Calculate annual totals
            annual_query = '''
                SELECT 
                    SUM(tax_deductions) as annual_taxes,
                    SUM(gross_pay) as annual_gross,
                    COUNT(DISTINCT employee_id) as unique_employees
                FROM payroll 
                WHERE strftime('%Y', pay_period_start) = ?
            '''
            
            annual_data = execute_query(annual_query, (str(year),))
            
            return {
                'success': True,
                'tax_summary': {
                    'year': year,
                    'annual_totals': annual_data[0] if annual_data else {},
                    'monthly_breakdown': monthly_data
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating tax summary: {str(e)}'
            }

    def calculate_employee_ytd(self, employee_id, year):
        """Calculate year-to-date totals for an employee"""
        try:
            query = '''
                SELECT 
                    SUM(gross_pay) as ytd_gross,
                    SUM(tax_deductions) as ytd_taxes,
                    SUM(deductions) as ytd_deductions,
                    SUM(net_pay) as ytd_net,
                    COUNT(*) as pay_periods
                FROM payroll 
                WHERE employee_id = ? AND strftime('%Y', pay_period_start) = ?
            '''
            
            results = execute_query(query, (employee_id, str(year)))
            
            if results:
                return {
                    'success': True,
                    'ytd_summary': results[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'No payroll data found for employee'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating YTD: {str(e)}'
            }