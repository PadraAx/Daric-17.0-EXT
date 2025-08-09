# -*- coding: utf-8 -*-
{
    'name': 'Employee Advance Salary Requests',
    'version': '17.0.0.0',
    'summary': 'Manage advance salary requests with approval workflows in HR and Payroll.',
    'description': """
This module allows employees to request advance salary with multi-level approvals (Department Manager, HR, Director) and integrates with accounting and payroll.
Key Features:
- Advance salary request
- Salary limit based on job position
- Department, HR, Director approvals
- Accounting and payroll integration
- Access controls and reporting
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'category': 'Human Resources',
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'account',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/advance_salary_view.xml',
        'views/inherite_hr_job_view.xml',
        'views/salary_rule.xml',
        'report/report_views.xml',
        'report/advance_salary_report.xml',
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
    'price': 0.0,
    'currency': '',
    'live_test_url': 'https://youtu.be/lYzufOFLtZc',
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_hook': '',
    'sequence': 0,
    'icon': '',
    'bootstrap': False,
}
