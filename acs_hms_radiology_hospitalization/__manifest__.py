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
    'name': 'Hospital Radiology Management - Hospitalization',
    'summary': 'Manage Radiology requests, Radiology tests flow on - Hospitalization.',
    'description': """
        This module add functionality to manage Radiology flow. radiology management system
        Hospital Management lab tests radiology invoices radiology test results ACS HMS
        - Hospitalization with Radiology Tests
    """,
    'version': '1.0.1',
    'category': 'HMS/Medical',
    'author': 'TORAHOPER',
    'support': 'info@almightycs.com',
    'website': 'https://torahoper.ir',
    'license': 'OPL-1',
    'depends': ['acs_hms_hospitalization','acs_hms_radiology'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'report/report_acs_radiology_prescription.xml',
        'report/discharge_summary_report.xml',
        'report/radiology_report.xml',

        'views/hms_base_view.xml',
        'views/radiology_view.xml',
    ],
    'images': [
        'static/description/hms_radiology_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'price': 16,
    'currency': 'USD',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: