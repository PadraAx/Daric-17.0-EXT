# -*- coding: utf-8 -*-
{
    'name': "User Audit",  # Module title
    'summary': "Monitor All Action that contain create, unlink and write",  # Module subtitle phrase
    'description': """
    Monitor All Action that contain create, unlink and write.
    Contain overwrite basic module, store actions information and exclude list that contain of modules that not supposed to store their actions."
    """,
    'category': 'System Administration/Users Access Management',
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'version': '1.0.0',
    'depends': [ 'base'],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/audit_log_views.xml',
        'views/user_audit_menu.xml',
    ],
    "assets": {
        "web.assets_backend": [
            'user_audit/static/src/img/**/*',
        ],
    },
    "application": True,
    'installable': True,

}

