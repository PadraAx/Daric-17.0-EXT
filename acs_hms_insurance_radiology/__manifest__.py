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
    'name': 'Radiology Insurance Management System',
    'summary': 'Patient Insurance Management for Radiology and related Claims',
    'description': """
        Patient Insurance Management for Radiology and related Claims. Hospital Management with Insurance Claim. ACS HMS
    """,
    'category': 'HMS/Medical',
    'version': '1.0.3',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ['acs_hms_radiology', 'acs_hms_insurance'],
    'data': [
        'security/ir.model.access.csv',
        'views/hms_base_view.xml',
        'views/insurance_view.xml',
    ],
    'images': [
        'static/description/hms_insuranceacs_almightycs_odoo_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 3,
    'price': 11,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: