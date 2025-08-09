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
    'name': "Web Timer Widget",
    
    'summary': """Add timer widget on web view.""",
    'description': """This module widget which allows you to set timer on any field by passing your start and end date as parameter. start stop timer working time""",
    'category': "HMS/web",
    'version': "1.0.1",
    "website": 'https://torahoper.ir',
    'author': 'TORAHOPER',
    'support': 'info@almightycs.com',
    'license': 'OPL-1',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'web_timer_widget/static/src/js/acs_timer.js',
            'web_timer_widget/static/src/js/acs_timer.xml',
        ]
    },
    'images': [
        'static/description/timer.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    "price": 14,
    "currency": "USD",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: