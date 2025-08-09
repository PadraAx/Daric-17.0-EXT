# -*- coding: utf-8 -*-
{
    "name": "Knowledge Base System",
    "version": "17.0.1.3.8",
    "category": "Productivity/Knowledge",
    "author": "TORAHOPER",
    "website": "https://torahoper.ir",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail",
        "web_editor",
        "web"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/report_paperformat.xml",
        "views/res_config_settings.xml",
        "views/ir_attachment.xml",
        "views/knowsystem_section.xml",
        "views/knowsystem_tag.xml",
        "views/knowsystem_tour.xml",
        "views/knowsystem_article_revision.xml",
        "views/knowsystem_article.xml",
        "views/knowsystem_article_template.xml",
        "wizard/create_from_template.xml",
        "reports/article_report_template.xml",
        "reports/article_report.xml",
        "wizard/article_section_update.xml",
        "wizard/article_tags_update.xml",
        "wizard/add_to_tour.xml",
        "wizard/article_search.xml",
        "wizard/article_groups_update.xml",
        "views/menu.xml",
        "data/cron.xml",
        "data/data.xml",
        "data/mass_actions.xml",
        "views/editor/options.xml",
        "views/editor/snippets.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "knowsystem/static/src/components/knowsystem_manager/*.xml",
                "knowsystem/static/src/components/knowsystem_manager/*.js",
                "knowsystem/static/src/components/knowsystem_jstree_container/*.xml",
                "knowsystem/static/src/components/knowsystem_jstree_container/*.js",
                "knowsystem/static/src/components/knowsystem_learning_tours/*.xml",
                "knowsystem/static/src/components/knowsystem_learning_tours/*.js",
                "knowsystem/static/src/components/knowsystem_navigation/*.xml",
                "knowsystem/static/src/components/knowsystem_navigation/*.js",
                "knowsystem/static/src/components/systray_quick_link/*.xml",
                "knowsystem/static/src/components/systray_quick_link/*.js",
                "knowsystem/static/src/components/action_menus/*.xml",
                "knowsystem/static/src/components/action_menus/*.js",
                "knowsystem/static/src/components/activity_menu_view/*.js",
                "knowsystem/static/src/components/activity_menu_view/*.xml",
                "knowsystem/static/src/components/activity_menu_view/*.scss",
                "knowsystem/static/src/services/*.js",
                "knowsystem/static/src/views/dialogs/knowsystem_dialog/*.js",
                "knowsystem/static/src/views/dialogs/knowsystem_dialog/*.xml",
                "knowsystem/static/src/views/dialogs/kms_export_dialog/*.js",
                "knowsystem/static/src/views/search/*.js",
                "knowsystem/static/src/views/kanban/*.xml",
                "knowsystem/static/src/views/kanban/*.js",
                "knowsystem/static/src/views/kanban/*.scss",
                "knowsystem/static/src/views/form/*.xml",
                "knowsystem/static/src/views/form/*.js",
                "knowsystem/static/src/views/fields/html_reference/*.js",
                "knowsystem/static/src/views/fields/knowsystem_many2many/*.js",
                "knowsystem/static/src/views/fields/knowsystem_many2many/*.scss",
                "knowsystem/static/src/views/fields/favorite_button/*.js",
                "knowsystem/static/src/views/fields/favorite_button/*.xml",
                "knowsystem/static/src/views/fields/like_button/*.js",
                "knowsystem/static/src/views/fields/like_button/*.xml",
                "knowsystem/static/src/views/fields/revisions_table/*.js",
                "knowsystem/static/src/views/fields/revisions_table/*.xml",
                "knowsystem/static/src/views/fields/revisions_table/*.scss",
                "knowsystem/static/src/views/fields/knowsystem_html/*.js",
                "knowsystem/static/src/views/fields/knowsystem_editor/*.xml",
                "knowsystem/static/src/views/fields/knowsystem_editor/*.js",
                "knowsystem/static/src/views/fields/knowsystem_editor/*.scss",
                "knowsystem/static/src/knowsystem_editor/knowsystem_for_backend.scss"
        ],
        "web.assets_frontend": [
                "knowsystem/static/src/knowsystem_editor/knowsystem_for_backend.scss"
        ],
        "web.report_assets_common": [
                "knowsystem/static/src/knowsystem_editor/knowsystem_for_backend.scss"
        ],
        "knowsystem.assets_editor": [
                "knowsystem/static/src/knowsystem_editor/knowsystem_editor_snippets_styles.scss"
        ],
        "knowsystem.editor_ui": [
                "knowsystem/static/src/knowsystem_editor/knowsystem_editor_ui.scss"
        ],
        "knowsystem.iframe_css_assets_edit": [
                [
                        "include",
                        "knowsystem.assets_editor"
                ],
                [
                        "include",
                        "knowsystem.editor_ui"
                ],
                [
                        "include",
                        "web.assets_common"
                ],
                [
                        "include",
                        "web.assets_frontend"
                ],
                [
                        "include",
                        "web/static/lib/bootstrap/scss/_variables.scss"
                ],
                [
                        "include",
                        "web_editor.backend_assets_wysiwyg"
                ],
                [
                        "include",
                        "web_editor.assets_legacy_wysiwyg"
                ],
                "knowsystem/static/src/wysiwyg/knowsystem_style.scss"
        ],
        "knowsystem.iframe_css_assets_edit_website": [
                [
                        "include",
                        "knowsystem.editor_ui"
                ],
                [
                        "include",
                        "web.assets_common"
                ],
                [
                        "include",
                        "web.assets_frontend"
                ]
        ],
        "web_editor.backend_assets_wysiwyg": [
                "knowsystem/static/src/wysiwyg/knowsystem_wysiwyg.js",
                "knowsystem/static/src/wysiwyg/knowsystem_wysiwyg.scss",
                "knowsystem/static/src/wysiwyg/wysiwyg.js"
        ],
        "knowsystem.assets_wysiwyg": [
                "knowsystem/static/src/wysiwyg/knowsystem_snippets.js"
        ],
        "web_editor.assets_legacy_wysiwyg": [
                "knowsystem/static/src/wysiwyg/snippets.editor.js"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to build a deep and structured knowledge base for internal and external use. Knowledge System. KMS. Wiki-like revisions. Knowledge management solution. Notion features. Docket features. Helpdesk knowledge. Collaborative library. Knowledge-based. Internal wiki. Documentation online. Knowledge online.",
    "description": """For the full details look at static/description/index.html
* Features * 
- Single-view knowledge navigation
- Fast, comfortable, and professional knowledge recording
- Get benefit from your knowledge
- &lt;i class=&#39;fa fa-dedent&#39;&gt;&lt;/i&gt; Website documentation builder
- &lt;i class=&#39;fa fa-globe&#39;&gt;&lt;/i&gt; Partner knowledge base portal and public knowledge system
- Interactive and evolving knowledge base
- &lt;i class=&#39;fa fa-info-circle&#39;&gt;&lt;/i&gt; Design eCommerce FAQ or documentation
- Any business and functional area
- &lt;i class=&#39;fa fa-gears&#39;&gt;&lt;/i&gt; Custom knowledge system attributes
- Secured and shared knowledge
#odootools_proprietary""",
    "images": [
        "static/description/main.png"
    ],
    "price": "268.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=83&ticket_version=17.0&url_type_id=3",
}