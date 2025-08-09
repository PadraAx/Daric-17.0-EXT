{
    "name": "Planning Extra",
    "version": "17.1",
    "license": 'LGPL-3',
    "category": 'Human Resources',
    "summary": "Planning Extra",
    "author": "TORAHOPER",
    'website': "https://daric-saas.ir",
    "depends": [
        "planning", "hr_payroll_ext"
    ],
    "data": [
        # security
        'security/ir.model.access.csv',
        'security/planning_security.xml',

        # wizard

        # view
        'view/planning_views.xml',

        # report

        # Menu
        'view/planning_menu.xml',

        # data
        
    ],
    "installable": True,
    'application': False,
    'auto_install': False,
}
