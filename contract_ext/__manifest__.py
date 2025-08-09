# -*- coding: utf-8 -*-
{
    'name': 'Contract Extra',
    'version': '17.1',
    'summary': 'Enhance employee contracts with additional features and views.',
    'description': """
This module extends the HR contract management with extra views and functionalities to support advanced HR operations.
Key Features:
- Additional menus for HR contracts
- Security rules and access controls
- Extended contract data structures
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr_contract',
        'employee_ext',
        'hr_contract_reports',
        'hr_skills',
    ],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_menu.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'images': [],
    'external_dependencies': {},
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': '',
    'live_test_url': '',
    'pre_init_hook': '',
    'post_init_hook': '',
    'uninstall_hook': '',
    'sequence': 0,
    'icon': '',
    'bootstrap': False,
}
