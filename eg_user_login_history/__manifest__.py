{
    'name': 'Users Login History',
    'version': '17.0',
    'category': 'System Administration/Users Access Management',
    'summary': 'Users Login History',
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'depends': ['base', 'mail'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/user_attendance.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
