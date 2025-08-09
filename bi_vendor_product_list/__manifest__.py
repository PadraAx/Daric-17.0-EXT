# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendors Product List | Vendor Product Management',
    'version': '17.0.0.0',
    'category': 'Inventory/Purchase',
    'summary': 'Product List in Vendor Product List Form Purchase Product List for Supplier Product Management Product List in Supplier Form Purchase Order Product List for RFQ List of Products for PO Products List Supplier Product List Product Vendors Associated Products',
    'description' :"""
        
        Vendors Product List Odoo App helps users to show all the product list in vendor form. Product should be visible along with product variant, minimum quality, price and delivery lead time so the user will get the idea of all those product associated with which vendors.       
    
    """,
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'depends': ['base','purchase'],
    'data': [
            'views/res_partner.xml',
    ],
    'license':'OPL-1',
    'installable': True,
    "application": True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/T7iJMPh7NaE',
    "images":['static/description/Vendors-Product-List-Banner.gif'],
}
