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
    'name' : 'Hospital WhatsApp Notification',
    'summary': 'Send WhatsApp notification to patient on Patient creation and Appointment Confirmation.',
    
    'description': """
        Hospital Message Notification, Hospital Management system acs hms medical appointment notification
    """,
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'license': 'OPL-1',
    'depends' : ['acs_whatsapp','acs_hms','acs_whatsapp_meta'],
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    
    "data": [
        "data/data.xml",
        "views/company_view.xml",
        "views/acs_hms_view.xml",
    ],
    'images': [
        'static/description/acs_hms_whatsapp_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 20,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
