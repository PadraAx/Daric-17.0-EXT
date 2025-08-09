# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'eLearning Ext',
    'category': 'Website',
    "author"  :  "TORAHOPER",
    'website': "https://torahoper.ir",
    'summary': 'Manage and publish an eLearning platform Ext',
    'installable': True,
    'depends': ['website_slides'],
    'data': [
        'security/ir.model.access.csv',
        'views/slide_slide_views.xml',
    ],
    "application":  True,
    'license': 'LGPL-3',
}
