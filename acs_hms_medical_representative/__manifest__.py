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
    'name': 'Medical Representative',
    'summary': 'Manage Medical Representative data and their visits for Hospital.',
    'description': """
        Functionality to manage Medical Representative data and their visits 
        acs hms hospital management system medical represenative
    """,
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ["acs_hms"],
    'data' : [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/mr_view.xml',
        'views/res_config_view.xml',
        'views/menu_item.xml',
    ],
    'images': [
        'static/description/hms_medical_representative_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 2,
    'price': 25,
    'currency': 'USD',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: