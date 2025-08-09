{
    'name': 'SMS Integration with sms.ir',
    'version': '1.0',
    'category': 'System Administration/Integration',
    'summary': 'Integrates Sms.ir SMS service with Odoo and supports OTP login.',
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'depends': ['base', 'website'],  # Removed 'smsir' from here
    'data': [
        'views/sms_integration_views.xml',
        'views/sms_integration_config_view.xml',
        'views/sms_integration_otp_views.xml',
        'data/sms_integration_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': ['smsir'],  # Keep 'smsir' here for Python package dependency
    },
    'description': """
        Integrates Sms.ir SMS service with Odoo and provides OTP-based login.
    """,
    'icon': '/sms_integration/static/description/logo.png',
}
