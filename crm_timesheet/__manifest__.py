# -*- coding: utf-8 -*-
{
    'name': 'CRM Timesheet',
    'version': '17.0.1.0.1',
    'summary': 'Track timesheets directly from CRM opportunities and activities.',
    'description': """
This module links CRM opportunities with timesheet records, allowing users to track time spent on leads and activities directly within the CRM.
Key Features:
- Log timesheets from CRM leads
- Timesheet entries linked with activities
- Improve time tracking for sales operations
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'AGPL-3',
    'category': 'Customer Relationship Management',
    'depends': [
        'crm',
        'project_timesheet_time_control',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/hr_timesheet_view.xml',
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
