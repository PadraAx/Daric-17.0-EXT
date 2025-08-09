# -*- coding: utf-8 -*-
{
    'name': "Export Access",

    'summary': "",

    'description': """ """,

    "author": "TORAHOPER",
    "website": "https://torahoper.ir",

    'category': 'System Administration/Users Access Management',
    "application": True,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],

    # always loaded
    'data': [
        'security/access.xml',
        'views/ir_exports_views.xml',
        'menu.xml',
    ],
    'assets':{
        'web.assets_backend': [
            ('replace','web/static/src/views/view_dialogs/export_data_dialog.js','export_access/static/src/export_data_dialog.js'),
            'export_access/static/src/export_data_dialog.xml'
        ]
    }
}

