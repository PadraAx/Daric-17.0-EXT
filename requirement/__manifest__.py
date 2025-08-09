# -*- coding: utf-8 -*-
{
    'name': "DTM",  # Module title
    'author': 'Daric',
    'summary': "DTM",  # Module subtitle phrase
    'description': """
    Business Requirement Analysis"
    """,  # Supports reStructuredText(RST) format  ,'rowno_in_tree'
    "category": "Governance/Digital Transformation Management",
    'website': 'https://daric-saas.ir',
    'version': '1.0.0',
    'depends': ['base_setup','web','mail','project'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/requirement_business_requirement_analysis_menu.xml',
        'wizard/review_create_wizard_view.xml',
        'wizard/extract_relationships_views.xml',
        'views/requirement_business_domain_categories_view.xml',
        'views/requirement_business_domains_integration.xml',
        'views/requirement_business_domain_view.xml',
        'views/requirement_assignments_view.xml',
        'views/requirement_feature_category_view.xml', 
        'views/requirement_feature_view.xml', 
        'views/requirement_requierment_view.xml',
        'views/requirement_review_view.xml',
        # 'views/solution_type_view.xml',
        'views/requirement_solution_view.xml',
        'views/requirement_critical_level_view.xml',
        'views/requirement_tag_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            #  'business_requirement_analysis/static/src/js/control_panel_button.js',
              '/requirement/static/src/css/custom.css',
        ],
     },
    
}

