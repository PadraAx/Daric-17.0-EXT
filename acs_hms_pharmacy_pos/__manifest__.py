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
    'name': 'Hospital Pharmacy Management - Point of Sale',
    'summary': 'Link module between Point of Sale and Hospital Pharmacy Management system',
    'description': """ Link module between Point of Sale and Hospital Pharmacy Management system. Posnt of prescription integration with Hospital management system.
""",
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ['acs_hms_pharmacy', 'point_of_sale'],
    'data': [
        'data/acs_hms_pharmacy_pos_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/prescription_order_views.xml',
        'views/pos_order_views.xml',
        'views/stock_template.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'acs_hms_pharmacy_pos/static/src/**/*',
        ],
    },
    'images': [
        'static/description/hms_pharmacy_pos_almightycs_odoo_cover.jpg',
    ],
    'sequence': 2,
    'price': 260,
    'currency': 'USD',
    'installable': True,
    'auto_install': False,

}
