# -*- coding: utf-8 -*-
{
    'license': 'LGPL-3',
    'name': "Web Window Title",
    'summary': "The custom web window title",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'support': 'i@renjie.me',
    'category': 'System Administration/Backend UI',
    'version': '1.1',
    'depends': ['base_setup'],
    'demo': [
        'data/demo.xml',
    ],
    'data': [
        'views/res_config.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'assets': {
        'web.assets_backend': [
            'web_window_title/static/src/js/web_window_title.js',
        ],
    },
    'installable': True,
    'auto_install': True,
    "application": True,
}