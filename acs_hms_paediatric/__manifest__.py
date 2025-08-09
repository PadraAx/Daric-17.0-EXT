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
    'name': 'Hospital Management System for Paediatrics ( Pediatric )',
    'summary': 'Hospital Management System for Paediatrics',
    'description': """
                Hospital Management System for Paediatrics pediatric. HealthCare Gynec system for hospitals
                With this module you can manage :
                - Child Patients
                - Maintain Child Growth Register
                - Child Vaccination
                acs hms almightycs
    """,
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'author': 'TORAHOPER',
    'support': 'info@almightycs.com',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ['acs_hms_vaccination'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/weight_data.xml',
        'data/height_data.xml',
        'data/head_data.xml',
        'data/data.xml',
        'views/acs_hms_views.xml',
        'views/hms_paediatric_view.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/hms_paediatric_almightycs_cover.jpeg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 101,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: