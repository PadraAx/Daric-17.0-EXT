# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Stages',
    'version': '7.1.2',
    'license': 'Other proprietary',
    'depends': [
        'project',
    ],
    'category': 'Services/Project',
    'summary':  """Show stages on project form.""",
    'description': """
       This app allows you to show stages on project
project stages
stage project
    """,
    
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'images': ['static/description/ps99.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_stages_odoo/927',#'https://youtu.be/-oBtmMJ_28c',
    'data': [
        'security/ir.model.access.csv',
        'views/project_stage_view.xml',
        'views/project_view.xml',
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
