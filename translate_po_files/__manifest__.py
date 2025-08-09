# -*- coding: utf-8 -*-
{
    'name': "Translate PO Files",
    'summary': """The Translate PO files Application is a powerful and user-friendly software tool designed to 
    streamline and simplify the process of translating Portable Object (PO) files.
    """,
    'description': """The Translate PO files Application is a powerful and user-friendly software tool designed to 
    streamline and simplify the process of translating Portable Object (PO) files. These files are commonly used in 
    software development for managing text translations, making them an essential component for creating multilingual 
    applications.
    The Translate PO files Application is an indispensable tool for software developers, localization teams, and anyone 
    involved in translating content for international audiences. 
    """,
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    'category': 'System Administration/Translation',
    'version': '17.0.0.1.0',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': ['polib', 'deep-translator'],
    },
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/po_file_translator_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    "application": True,
    'auto_install': True,  
}
