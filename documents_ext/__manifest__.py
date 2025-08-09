# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Documents Ext',
    'category': 'Documents',
    'summary': 'Documents Ext',
    'installable': True,
    'depends': ['documents'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/documents_folder_views.xml',
        'views/documents_document_views.xml',
    ],
     'assets': {
        'web.assets_backend': [
            'documents_ext/static/src/xml/documents_inspector.xml',
            'documents_ext/static/src/js/documents_inspector.js',
            'documents_ext/static/src/js/documents_search_panel.js',
        ],
    },
    'license': 'LGPL-3',
}
