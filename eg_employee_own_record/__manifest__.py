# -*- coding: utf-8 -*-
{
    'name': 'Employee Own Record',
    'version': '17.0',
    'summary': 'Allow employees to view and manage their own HR records securely.',
    'description': """
This module allows employees to access and manage their own HR records with restricted access for better data security and privacy.
Key Features:
- Employees can view their own profiles
- Access controlled via security rules
- Enhances HR data privacy
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'category': 'Other',
    'depends': [
        'hr',
    ],
    'data': [
        'security/hr_employee_security.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'images': [
        'static/description/banner.png',
    ],
    'external_dependencies': {},
    'installable': True,
    'application': True,
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
