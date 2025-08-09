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
#CODE Reference taken from GNU HEALTH for disease and category.
{
    'name' : 'International Classification of Diseases (ICD10)',
    'summary': 'International Classification of Diseases and Diseases Category (ICD10).',
    'description': """
        International Classification of Diseases, AlmightyCS acs hms icd10 hospital management system
    """,
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'license': 'OPL-1',
    'depends' : ['acs_hms'],
    'author': 'TORAHOPER',
    'website': 'https://torahoper.ir',
    
    "data": [
        "data/disease_categories.xml",
        "data/diseases.xml",
    ],
    'images': [
        'static/description/acs_hms_icd10_almightycs_cover.jpg',
    ],
    "cloc_exclude": [
        "data/*.xml",
    ],
    'installable': True,
    'application': False,
    'sequence': 2,
    'price': 15,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: