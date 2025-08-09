# -*- coding: utf-8 -*-
{
    'name': 'User Access Manager',
    'summary': 'Manage user access rights, control menu visibility, and set field-level permissions in Daric.',
    'category': 'System Administration/Users Access Management',
    'version': '17.0.0.0',
    'sequence': 1,
    "author": "TORAHOPER",
    'license': 'OPL-1',
    "website": "https://torahoper.ir",
    'maintainer': 'Daric',
    'support': 'support@daric-saas.ir',
    'description': """
        The User Access Manager simplifies user access management in Daric, allowing businesses to control access rights seamlessly:
        - Hide menus, buttons, tabs, and fields.
        - Manage model-level access (create, edit, delete, duplicate, export).
        - Set domain-based conditional access rights.
        - Make fields invisible, read-only, or required.
        - Control chatter access and restrict import/export actions.
        - Disable login for specific users or enable read-only mode.

        Designed to be user-friendly, this tool provides powerful customization without requiring technical expertise.

        Translations available in:
        - English, French, Arabic, Chinese, Spanish.

        Learn more at: [Daric SaaS](https://daric-saas.ir)
    """,
    'depends': [
        'base',
        'auth_signup',
        'web',
        'base_setup'
    ],
    'external_dependencies': {
        'python': [
            'openpyxl',
            'werkzeug',
            'lxml'
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/ir_module_category.xml',
        'data/user_profiles_cron.xml',
        'data/password_expire_mail.xml',
        'views/menu.xml',
        'views/res_users_view.xml',
        'views/user_profiles.xml',
        'views/res_groups.xml',
        'views/user_management_view.xml',
        'views/reset_password.xml',
        'views/general_settings_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'access_users_manager/static/src/js/hide_action_buttons.js'
        ],
        'web.assets_frontend': [
            'access_users_manager/static/src/js/eye_slash.js'
        ]
    },
    'images': [
        'static/description/module_image.png'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'access_post_install_report_action_hook'
}
