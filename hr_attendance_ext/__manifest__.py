# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Attendances Ext',
    'category': 'Human Resources',
    'author': 'Daric',
    'website': "https://daric-saas.ir",
    'summary': 'Track employee attendance',
    'installable': True,
    'depends': [
        'hr_attendance', 'hr_attendance_gantt', 'hr_work_entry', 'hr_payroll_ext', 'timesheet_grid'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/hr_attendance_security.xml',
        # view
        'views/hr_attendance_rule_views.xml',
        'views/hr_attendance_punch_views.xml',
        'views/hr_attendance_missing_views.xml',
        'views/hr_attendance_view.xml',
        'views/hr_attendance_gantt.xml',
        'views/attendance_menu_views.xml',
        'views/res_users_views.xml',
        # wizard
        'wizard/hr_attendance_regeneration_wizard_views.xml',
        # data
        'data/hr_work_entry_type.xml',
        'data/hr_mnm_attendance_rule.xml',
        'data/hr_hc_attendance_rule.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'hr_attendance_ext/static/src/js/**/*',
        ],
    },
    'license': 'LGPL-3',
}
