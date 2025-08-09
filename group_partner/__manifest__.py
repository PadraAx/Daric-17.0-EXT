# -*- coding: utf-8 -*-

{
    "name": "Customer group",
    "version": '17.0',
    "depends": ["base", "account"],
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "support": "sogesi@sogesi-dz.com",
    'category': 'Sales/CRM',
    "summary": """This module allows to assign partners to a group """,
    "description": """This module allows to assign partners to a group """,
    'images': ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/res_partner_group.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}
