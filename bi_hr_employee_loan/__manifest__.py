# -*- coding: utf-8 -*-
{
    'name': 'Employee Loan Management',
    'version': '17.0.0.0',
    'summary': 'Manage employee loan requests, approvals, disbursements, and repayments integrated with payroll.',
    'description': """
This module allows HR to manage employee loan requests, approvals, disbursements, and repayments through payroll or cash/bank, including loan types, policies, and reports.
Key Features:
- Loan request and multi-step approval
- Loan disbursement by accountant
- Repayment through payroll integration
- Repayment via cash/bank
- Manage loan proofs, types, and policies
- Generate loan reports and installment schedules
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'category': 'Human Resources',
    'depends': [
        'base',
        'hr',
        'portal',
        'utm',
        'account',
        'hr_payroll',
        'hr_payroll_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/loan_proof_view.xml',
        'views/loan_request_view.xml',
        'views/loan_type_view.xml',
        'views/loan_policies_view.xml',
        'views/loan_installment_view.xml',
        'views/employee_views.xml',
        'views/account_payment_view.xml',
        'views/loan_rules.xml',
        'wizard/reject_request.xml',
        'report/report_views.xml',
        'report/print_loan_report.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'images': [
        'static/description/icon.png',
    ],
    'external_dependencies': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 39.0,
    'currency': 'EUR',
    'live_test_url': 'https://youtu.be/rTW20wwm78U',
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_hook': '',
    'sequence': 0,
    'icon': '',
    'bootstrap': False,
}
