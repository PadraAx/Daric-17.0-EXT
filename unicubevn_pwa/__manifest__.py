# -*- coding: utf-8 -*-
{
    'name': "Utilities: Config PWA",

    'summary': """
        This is the custom module for configuring builtin Odoo PWA.
        """,

    'description': """
        This is the custom module for configuring builtin Odoo PWA, including:
            - Change PWA icon
            - Add custom path
    """,

    "author": "TORAHOPER",
    "license": "LGPL-3",
    'category': 'System Administration/Backend UI',
    'version': '17.0.0.1',
    "website": "https://torahoper.ir",
    'support': 'community@unicube.vn',
    "application": True,
    "installable": True,

    # any module necessary for this one to work correctly
    'depends': ['web'],

    "images": ["static/description/image.jpg"],

    # always loaded
    'data': [
        'views/res_config.xml',
    ],
}
