# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Advance Expense Request',
    'version': '17.0.0.0',
    'summary': 'Manage employee advance expense requests with approval and accounting integration.',
    'description': """
This module allows employees to request advance expenses with manager approval and accounting integration. Supports multi-currency without altering standard accounting entries.
Key Features:
- Advance expense request by employees
- Multi-currency support
- Approval workflow (Manager, HR)
- Integrated with HR Expenses and Accounting
- Defined reports and printable advance expenses
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'category': 'Human Resources',
    'depends': [
        'base',
        'account',
        'hr_expense',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/advance_expense_views.xml',
        'views/expence_inherit_view.xml',
        'report/report_views.xml',
        'report/advance_expence_report.xml',
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
    'live_test_url': 'https://youtu.be/18MNZMwmmFM',
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_hook': '',
    'sequence': 0,
    'icon': '',
    'bootstrap': False,
}
