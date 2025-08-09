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
    'name': 'HMS Operation Theater Booking',
    'summary': 'Manage Operation Theater Advance booking in Hospital to utilize OT more efficiently',
    'description': """
    HMS Operation Theater Booking almightycs odoo acs hms medical hospital management system
    Manage Operation Theater Advance booking in Hospital to utilize OT more efficiently
    """,
    'category': 'HMS/Medical',
    'version': '1.0.1',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ['acs_hms_hospitalization'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'reports/ot_report_template.xml',
        'wizard/ot_report_views.xml',
        'views/ot_view.xml',
        'views/hms_base.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/acs_hms_operation_theater_almightycs_odoo_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 36,
    'currency': 'USD',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
