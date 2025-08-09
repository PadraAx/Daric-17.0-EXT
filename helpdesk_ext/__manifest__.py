# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Ext',
    'author': 'TORAHOPER',
    'website': "https://torahoper.ir",
    'version': '1.6',
    'description': """
    Feedback system"
    """,  # Supports reStructuredText(RST) format
    'category': 'Services/Helpdesk',
    'version': '1.0.0',
    'depends': ['helpdesk', 'web_enterprise', 'website_helpdesk'],
    'data': [
        # Security
        # 'security/ir.model.access.csv',
        'security/helpdesk_security.xml',
        
        # Views
        'views/helpdesk_ticket_views.xml',
        
    ],
    
    'assets': {
        'web.assets_backend': [
            'helpdesk_ext/static/src/webclient/user_menu/user_menu_items.js',
        ],
    },
    "application": True,
}
