{
    'name': 'SMS Integration with sms.ir',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Integrates Sms.ir SMS service with Odoo and supports OTP login.',
    'author': 'Daric',
    'depends': ['base', 'website', 'smsir-python'],
    'data': [
        'views/sms_integration_views.xml',
        'views/sms_integration_config_view.xml',
        'views/sms_integration_otp_views.xml',  # Include the OTP view XML
        'data/sms_integration_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': ['smsir-python'],
    },
    'description': """
        Integrates Sms.ir SMS service with Odoo and provides OTP-based login.
    """,
    'icon': '/sms_integration/static/description/logo.png',  # Add the icon path here
}
