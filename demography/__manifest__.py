# -*- coding: utf-8 -*-
{
    "name": "Demography",
    "summary": "",
    "description": """
""",
    "version": "17.0.1.0.0",
    "category": "Localization",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "LGPL-3",
    "depends": ["base", "mail", "geo_address"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/demog_views.xml",
        "views/demog_religion_views.xml",
        "views/demog_ethnic_group_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "images": ["static/description/icon.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
