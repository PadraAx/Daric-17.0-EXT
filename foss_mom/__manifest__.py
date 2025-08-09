# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Minutes of Meeting",
    'version': '17.0.0.0.0',
    'summary': """ Minutes of Meeting """,
    'author': 'Daric',
    'category': 'Productivity/Meeting',
    'website': "https://daric-saas.ir",
    'description': """
    """,
    'depends': ['base','calendar','project'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/mom_views.xml',
        'report/layout.xml',
        'report/reports.xml',
        'report/mom_report_template.xml',
        'data/foss_mom_email_template.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
