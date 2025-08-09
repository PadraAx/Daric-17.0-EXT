# -*- coding: utf-8 -*-
{
    'name': 'Product Code Generator',
    'version': '1.0',
    'summary': 'Generate unique product codes based on category and supplier in Daric.',
    'author': 'TORAHOPER',
    'category': 'Inventory/Product',
    'depends': ['base', 'product', 'stock', 'contacts'],
    'data': [
        'views/product_category_view.xml',
        'views/res_partner_view.xml',
        'views/product_template_view.xml',
        # 'data/product_category_data.csv',
        'data/product_category_data.xml',
    ],
    'website': 'https://torahoper.ir',
    'installable': False,
    "application": False,
    'images': ['static/description/image.png'],  # This sets the module icon
}
