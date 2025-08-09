{
    'name': 'Meeting Management',
    'version': '17.0',
    'category': 'Services/Appointment',
    'summary': 'Manage Minute Meeting in Calender',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'depends': ['calendar'],
    
    'data': [
        'security/ir.model.access.csv',
        'views/minute_meeting_view.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
