# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/


{
    'name': "Hide Menu",
    'summary': """
        Restrict Menu Items from Specific Users""",
    'description': """
        Restrict Menu Items from Specific Users""",
    "author": "TORAHOPER",
    'maintainer':'Kiran K',
    "website": "https://torahoper.ir",
    'images': ["static/description/banner.png"],
    'category': 'System Administration/Users Access Management',
    "application": True,
    'version': "17.0",
    'license': 'AGPL-3',
    'depends': [
        'base'
    ],
    'data': ['views/res_users.xml',
             ],
}
