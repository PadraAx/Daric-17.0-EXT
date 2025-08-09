# -*- coding: utf-8 -*-
{
    'name': "hr_skills_ext",
    'author': "Daric",
    'website': "https://daric-saas.ir",
    'summary': """ HR skill extract""",

    'description': """
        extract module for having some changes on hr_skill module
    """,

    
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_skills', 'employee_ext',],

    # always loaded
    'data': [
        # security
        'security/ir.model.access.csv',
        
        # views
        'views/hr_employee_views.xml',
        
        # Menu
        
    ],
    'assets': {
        'web.assets_backend': [
        ]
    }

}
