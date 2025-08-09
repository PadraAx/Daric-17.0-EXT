{
    'name': 'Cheque Number on Payment',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'This module allows to add cheque number and also image on Payment!',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'depends': ['account'],
    
    'data': [
        'reports/account_report_payment_receipt_templates.xml',
        'views/account_payment_view.xml',
        'wizard/account_payment_register_view.xml',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
