# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Work Entries - Contract Extra',
    'author': "Daric",
    'website': "https://daric-saas.ir",
    'category': 'Human Resources',
    'summary': 'Manage work entries',
    'installable': True,
    'depends': [
        'hr_work_entry_contract', 'planning_ext', 'hr_attendance_ext',
    ],
    'data': [
        # security
        "security/ir.model.access.csv",

        # views
        'views/hr_work_entry_views.xml',

        # data
        'data/ir_cron_data.xml',
    ],

    'license': 'LGPL-3',
}
