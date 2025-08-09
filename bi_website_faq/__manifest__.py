# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Website FAQ and Answers",
    "version" : "17.0.0.0",
    "category" : "Website",
    'license': 'OPL-1',
    'summary': 'Website Frequently Asked Questions Website FAQ page on website publish FAQ on website FAQ answer website FAQ questions and answer manage website FAQ with answer website FAQ menu for website web Frequently Asked Question on website',
    "description": """
    
        This odoo app helps user to add Frequently Asked Questions in the back-end and get them in a FAQ page on website, user can save time by giving answer of most commonly questions. User also have option to publish/Unpublish FAQ on website, user also can make attractive answer for FAQ as we have provided HTMl field for FAQ answer.
    
    """,
    "author": "TORAHOPER",
    "website" : "https://torahoper.ir",
    "depends" : ['website'],
    "data": [

        'security/ir.model.access.csv',
        'views/website_faq_template.xml',
        'views/website_faq_views.xml',
        
    ],
    "qweb" : [],
    "auto_install": False,
    'application': True,
    "installable": True,
    "live_test_url":'https://youtu.be/8I5s5mBP-sA',
    "images":["static/description/icon.png"],
     'assets':{
        'web.assets_frontend':[
            'bi_website_faq/static/src/scss/website_faq.scss',
            'bi_website_faq/static/src/js/website_faq.js',
        ]
    },
}
