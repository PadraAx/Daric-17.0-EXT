# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║               SOFTWARE DEVELOPED AND SUPPORTED BY                ║
#║          ALMIGHTY CONSULTING SOLUTIONS PRIVATE LIMITED           ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   https://torahoper.ir                     ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name' : 'Invoice Summary Report for Patient By AlmightyCS',
    'summary': 'Invoice Summary Report for Patient By AlmightyCS',
    'description': """Invoice Summary Report for Patient By AlmightyCS""",
    
    'category' : 'HMS/Extra Addons',
    'depends' : ['acs_hms', 'acs_invoice_summary'],
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    
    'data': [
        'views/hms_base.xml',
        'reports/report_invoice_summary.xml',
    ],
    'images': [
        'static/description/acs_hms_insurance_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 10,
    'currency': 'USD',

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: