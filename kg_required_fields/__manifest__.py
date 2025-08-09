# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/


{
    'name': "Required Fields Highlight",
    'summary': """
        Highlights all required fields in bold on any form, making it easy for users to quickly identify and fill out necessary information accurately.""",
    'description': """
        Highlights all required fields in bold on any form.""",
    "author": "TORAHOPER",
    'maintainer':'Kiran K',
    "website": "https://torahoper.ir",
    'images': ["static/description/banner.png"],
    'category': 'System Administration/Backend UI',
    'version': "17.0",
    "application": True,
    'license': 'AGPL-3',
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'kg_required_fields/static/scss/style.scss',
        ],
    },
    'data': [
             ],
}
