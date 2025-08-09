# -*- coding: utf-8 -*-
{
    "name": "Microsoft Office Preview",
    "version": "1.0.0",
    "category": "System Administration/Backend UI",
    "summary": "Allows you to preview Microsoft Office documents",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "images": ["static/description/module_banner.png", "static/description/icon.png"],
    "installable": True,
    "auto_install": False,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "/le_preview_microsoft_office/static/src/js/attachment.js",
            # "/le_preview_microsoft_office/static/src/js/attachment_viewer_viewable.js",
            "/le_preview_microsoft_office/static/src/scss/attachment_viewer.scss",
            "/le_preview_microsoft_office/static/src/xml/attachment_viewer.xml",
        ],
    },
    "license": "OPL-1",
    "price": 70.00,
    "currency": "EUR",
}
