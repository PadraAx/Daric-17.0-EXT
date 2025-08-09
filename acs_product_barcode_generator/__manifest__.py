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
    "name": 'ACS Product Barcode Generator',
    'summary': """This module will add a functionality to allow barcode generation of EAN13 for products. You can do configuration at product or category or company level.""",
    "description": """
    This module will add a functionality to allow barcode generation of EAN13 for products
    You can do configuration at product or category or company level.
    The 13rd is the key of the EAN13, this will be automatically computed.
    Barcode product barcode generator generate product barcode 
    """,
    "category" : "HMS/Warehouse",
    "version": '1.0.1',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    "depends": [ 'product'],
    "data": [
       "data/data.xml",
       "views/product_view.xml",
    ],
    'images': [
        'static/description/barcode_generator_cover_almightycs_odoo.jpg',
    ],
    'installable': True,
    'sequence': 2,
    'price': 12,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 