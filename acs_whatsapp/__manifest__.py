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
    'name' : 'WhatsApp Integration',
    'summary': 'Odoo WhatsApp Integration to send Watsapp messages from Odoo.',
    
    'description': """
        Odoo WhatsApp Integration to send Watsapp messages from Odoo. Notification WhatsApp to customer or users, Acs hms
    """,
    'category' : 'HMS/Extra Addons',
    'version': '1.0.3',
    'license': 'OPL-1',
    'depends' : ['hr'],
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "wizard/create_whatsapp_message_view.xml",
        "wizard/whatsapp_messages_view.xml",

        "views/message_template_view.xml",
        "views/message_view.xml",
        "views/announcement_view.xml",
        "views/partner_view.xml",
        "views/company_view.xml",
        "views/menu_item.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'acs_whatsapp/static/src/scss/custom_backend.scss',
        ]
    },
    'images': [
        'static/description/acs_odoo_whatsapp_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 41,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: