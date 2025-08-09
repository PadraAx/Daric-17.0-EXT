# -*- coding: utf-8 -*-
{
    'name': 'Session Management',
    'summary': 'Monitor user sessions, track logins, and audit user activity in Daric.',
    'category': 'System Administration/Users Access Management',
    'version': '17.0.1.0.0',
    'sequence': 6,
    "author": "TORAHOPER",
    'license': 'OPL-1',
    "website": "https://torahoper.ir",
    'maintainer': 'Daric',
    'support': 'support@daric-saas.ir',
    'description': """
        Manage user sessions and track login activity with detailed audit logs.  
        - Monitor logins with IP, device, and location details.  
        - Get real-time notifications for new sessions.  
        - Track user actions (create, update, delete) with logs.  
        - Ensure security and compliance with audit trails.  

        Learn more at: [Daric SaaS](https://daric-saas.ir).
    """,
    'depends': [
        'mail',
        'auth_oauth',
        'http_routing'
    ],
    'external_dependencies': {
        'python': [
            'user_agents'
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'data/cron.xml',
        'data/email_template.xml',
        'views/res_config_settings_view.xml',
        'views/login_log_view.xml',
        'views/activity_log_view.xml',
        'views/res_user_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'advanced_session_management/static/src/scss/style.scss',
            'advanced_session_management/static/src/js/router_service.js',
        ]
    },
    'images': [
        'static/description/banner.gif'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'live_test_url': 'https://daric-saas.ir/demo'
}
