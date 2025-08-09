# -*- coding: utf-8 -*-
{
    'name': "knowledge_ext",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Orielgrp",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['web', 'knowledge', 'hr', 'web_editor', 'website_knowledge'],

    # always loaded
    'data': [
        'security/knowledge_security.xml',
        'security/ir.model.access.csv',

        'views/knowledge_request_views.xml',
        # 'views/knowledge_template_views.xml',
        'views/knowledge_article_views.xml',
        'views/knowledge_request_score_views.xml',
        'views/knowledge_score_views.xml',
        'views/knowledge_tag_views.xml',
        'views/knowledge_request_ambassador_item_views.xml',
        'views/knowledge_ambassador_item_views.xml',

        'wizard/wizard_supervisor_mark.xml',
        'views/knowledge_ext_menus.xml',
        'views/knowledge_template_ext.xml',
        # 'wizard/wizard_template.xml',

        'data/mail_template_data.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'knowledge_ext/static/src/xml/sidebar_row_ext.xml',
            'knowledge_ext/static/src/xml/topbar_ext.xml',
            'knowledge_ext/static/src/component/sidebar/sidebar.js',
            'knowledge_ext/static/src/component/sidebar/sidebar_section_ext.xml',

            'knowledge/static/src/js/knowledge_controller.js',
            'knowledge_ext/static/src/xml/knowledge_controller.xml',
            'knowledge_ext/static/src/js/knowledge_article_controller.js',
            'knowledge_ext/static/src/js/knowledge_article_renderers.js',
            'knowledge_ext/static/src/js/knowledge_article_render.js',
            'knowledge_ext/static/src/js/website_knowledge.xml',
            'knowledge_ext/static/src/js/knowledge_cover_dialog.js',

            # 'knowledge_ext/static/src/components/sidebar/sidebar_row.xml',
            'knowledge_ext/static/src/css/knowledge_article_view.css',
            'knowledge_ext/static/src/js/knowledge_article_view.js',
            'knowledge_ext/static/src/js/sidebar_section.js',
            'knowledge_ext/static/src/js/knowledge_controller.js',
            'knowledge_ext/static/src/html_confirm_dialog/*.js',
            'knowledge_ext/static/src/html_confirm_dialog/*.xml',
            'knowledge_ext/static/src/component/**/*.js',
            'knowledge_ext/static/src/component/**/*.xml'

        ],

    },
}
