{
    'name': 'Sales Terms & Conditions',
    'version': '17.0',
    'category': 'Sales/Sales',
    'summery': 'Terms and Conditions on Sales Order',
    'author': 'TORAHOPER',
    'website': "https://torahoper.ir",
    'depends': ['sale_management'],

    'data': [
            'security/ir.model.access.csv',
            'views/sale_terms_and_conditions_view.xml',
            'views/sale_order.xml',
            'report/sale_order_report.xml',
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
