# -*- coding: utf-8 -*-

{
    'name': 'IT Asset Management',
    'version': '0.1',
    'category': 'Accounting/Asset',
    'summary': """IT Asset Management""",
    'description': """This module is used for infrastructure management. You can record assets, credentials and network and service specific details.""",
    'author': 'Doyenhub Software Solution',
    'company': 'Doyenhub Software Solution',
    'maintainer': 'Doyenhub Software Solution',
    'website': 'https://www.doyenhub.com/',
    "price": 11,
    "currency": 'USD',
    'depends': ['mail', 'base', 'hr', 'stock', 'product', 'purchase_stock'],
    'data': [
        'security/it_asset_security.xml',
        'security/ir.model.access.csv',

        'views/asset_component_views.xml',
        'views/asset_material_request_views.xml',
        'views/res_users_asset.xml',
        'views/res_config_settings_views.xml',
        'views/stock_location_views.xml',
        'views/product_template_views.xml',
        'views/stock_move_views.xml',
        'views/stock_quant_views.xml',

        'wizard/asset_return_wizard_views.xml',
        'wizard/asset_reassign_wizard_views.xml',
        'wizard/asset_retired_wizard_views.xml',

        'data/mail_template.xml',
        'data/stock_sequence_data.xml',
        'data/asset_component_sequence.xml',

        'views/asset_menu.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    "images": ['static/description/banner.png'],
    'license': 'OPL-1'
}
