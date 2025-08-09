# -*- coding: utf-8 -*-
{
    'name': "Telegram Project",
    'summary': "KTT telegram integration with project module.",
    "author": "TORAHOPER",
    'maintainer': 'Mai Văn Khai',
    "website": "https://torahoper.ir",
    "license": "LGPL-3", #"OPL-1",
    'images': ['images/telegram_and_odoo.gif'],
    'category': 'System Administration/Integration',
    'version':'17.0.1.0.2',
    # DEPENDS MODULES
    'depends': ['base', 'project'],
    # always loaded
    'data': [
        # ============================================================================================================
        # DATA
        # ============================================================================================================
        # SECURITY SETTING - GROUP - PROFILE

        # ============================================================================================================
        # WIZARD
        # ============================================================================================================
        # VIEWS
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        # ============================================================================================================
        # REPORT
        # ============================================================================================================
        # MENU - ACTION
        # ============================================================================================================
        # FUNCTION USE TO UPDATE DATA LIKE POST OBJECT
        # ============================================================================================================
    ],
    "application": True,
    'installable': True,
    #'currency': 'USD'
}
