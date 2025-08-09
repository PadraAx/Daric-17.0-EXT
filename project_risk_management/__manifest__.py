# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Project Risk Management",
    'version': '6.1.10',
    'license': 'Other proprietary',
    'author': "Daric",
    'website': "https://daric-saas.ir",
    'support': 'contact@probuse.com',
    'summary': 'This app allow your project team to have risk management application in Odoo.',
    'description': """
Risk Management
risk
risk Incidents
risk Incident
Incidents
Incident
project Incidents
project Incident
task Incidents
task Incident
Incidents app
project issue
issue
project risk
Strategic Risk
task risk
risk control
Operational Risk
risk app
project task risk
financial risks
identify the Risk
odoo risk management

""",
    'category' : 'Risks/Project Risk Management',
    'images': ['static/description/img1.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/project_risk_management/963',#'https://youtu.be/sekBoA2k6vI',
    'depends': ['project'],
    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/risk_task.xml',
        'wizard/project_project_view_wizard.xml',
        'views/risk_type_view.xml',
        'views/risk_management_view.xml',
        'views/risk_category_view.xml',
        'views/project_risk_line_view.xml',
        'views/project_project_view.xml',
        'views/project_task_risk_line_view.xml',
        'views/project_task_response.xml',

    ],
    'installable' : True,
    'application' : True,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

