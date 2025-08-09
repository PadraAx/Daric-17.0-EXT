# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                TORAHOPER               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://torahoper.ir                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝

{
    'name': 'Add Products by Barcode in Invoice',
    
    'summary': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.""",
    'description': """Add Products by scanning barcode to avoid mistakes and make work faster in Invoice.
    Barcode
    Product barcode
    barcode in invoice
    Invoice Barcode
    Scan barcode and add product
    Scan product and add
    Scan to add product
    Scan barcode to add product
    product by barcode scan
    add product in invoice""",
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'version': '1.0.1',
    'category': 'HMS/Accounting',
    'author': 'TORAHOPER',
    'support': 'info@almightycs.com', 
    "depends": ["account",'barcodes'],
    "data": [
        "views/account_invoice_view.xml",
    ],
    'images': [
        'static/description/barcode_cover.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 9,
    'currency': 'USD',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: