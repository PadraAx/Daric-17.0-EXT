# -*- coding: utf-8 -*-
{
    'name': 'Employee Loan Management with Payroll',
    'version': '7.1.3',
    'summary': 'Manage employee loans with payroll integration.',
    'description': """
This module integrates employee loans with the payroll system, enabling automatic deduction of loan installments from employee salaries.
It helps manage loans and payroll in one seamless system.
Key Features:
- Loan request and approval workflow
- Payroll integration for loan installment deductions
- Track loan balance and installments directly in payroll
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'Other proprietary',
    'category': 'Human Resources/Payroll',
    'depends': [
        'hr_payroll',
        'hr_employee_loan',
    ],
    'data': [
        'views/hr_salary_rule_view.xml',
        'views/hr_payslip_line_view.xml',
        'views/loan_installment_view.xml',
    ],
    'demo': [
        'data/loan_payroll_sequence_enterprice.xml',
    ],
    'images': [
        'static/description/img1.png',
    ],
    'price': 79.0,
    'currency': 'EUR',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/employee_loan_payroll_enterprise/430',
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {},
    'sequence': 0,
    'icon': '',
    'bootstrap': False,
}
