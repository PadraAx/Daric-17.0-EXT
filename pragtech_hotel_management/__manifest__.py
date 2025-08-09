{
    'name': 'Hotel Management',
    'version': '17.0.0.1',
    'category': 'Industries/Hospitality',
    'author': 'Daric',
    'website': 'https://daric-saas.ir',
    'summary': 'Hotel Management Module for Hotel/Resort/Property management. You can manage Configure Property Hotel Configuration Check In, Check out Manage Folio',
    "description": """
Module for Hotel/Resort/Property management. You can manage:
    * Configure Property
    * Hotel Configuration
    * Check In, Check out
    * Manage Folio
    * Payment

Different reports are also provided, mainly for hotel statistics.
""",
    "depends": ['base', 'stock', 'product', 'mrp', 'point_of_sale', 'web', 'website', 'payment'],
    'currency': 'USD',
    'price': 499,
    'images': ['static/description/img/Animated-odoo-hotel-management.gif'],
    # 'images': ['static/description/end-of-year-sale-main.jpg'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=Odoo-Hotel-Management',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
