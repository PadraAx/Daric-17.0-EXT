# -*- coding: utf-8 -*-
{
    'name': "Multi-Company Access Rights",

    'summary': """
        Different access rights for multi-company users, Restriction, Restricted, Privillage, Restricted Menu, Different Access, Different Rights, Rights, Access Rights, Limited Access, Limited Menu""",

    'description': """
        Allow users to have different access rights for each company
    """,

    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "OPL-1",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'System Administration/Users Access Management',
    'version': "17.0.1.1.9",

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_users.xml',
        'views/res_users_groups.xml',
        'views/res_users_groups_wizard.xml',
        'views/actions.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'oi_multi_company_access/static/src/switch_company_menu/switch_company_menu.js',
            'oi_multi_company_access/static/src/switch_company_menu/switch_company_menu.xml',
            'oi_multi_company_access/static/src/many2many_checkboxes_sorted/many2many_checkboxes_sorted.js',
            'oi_multi_company_access/static/src/webclient/company_service.js'
            ],
    },
    
    # only loaded in demonstration mode
    'demo': [
        
    ],
    "application": True,
    'images':[
        'static/description/cover.png'
    ]          
}