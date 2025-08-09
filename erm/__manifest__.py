# -*- coding: utf-8 -*-
{
    "name": "ERM",  # Module title
    'author': 'Daric',
    "summary": "Enterprise Risk Management(ERM)",  # Module subtitle phrase
    "description": """
        Enterprise Risk Management(ERM)
    """,  # Supports reStructuredText(RST) format  ,'rowno_in_tree'
    "category": "Risks/Enterprise Risks Management",
    'website': 'https://daric-saas.ir',
    "version": "1.0.0",
    "depends": ["base",'mail',],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/assessment_create_wizard_view.xml",
        "views/erm_menu.xml",
        "views/erm_risk_impact_view.xml",
        "views/erm_risk_likelihood_view.xml",
        "views/erm_risk_velocity_view.xml",
        "views/erm_risk_category_type_view.xml",
        "views/erm_risk_category_view.xml",
        "views/erm_risk_control_effectiveness_view.xml",
        "views/erm_risk_control_view.xml",
        "views/erm_risk_source_category_view.xml",
        "views/erm_risk_source_view.xml",
        "views/erm_risk_affected_area_view.xml",
        "views/erm_mitigation_action_plan_view.xml",
        "views/erm_risk_treatment_view.xml",
        "views/erm_risk_assessment_analysis_view.xml",
        "views/erm_risk_assessment_evaluation_view.xml",
        # 'views/erm_risk_assessment_view.xml',
        'views/erm_risk_assignment_view.xml',
        'views/erm_risk_tag_view.xml',
        'views/erm_risk_trigger_view.xml',
        'views/erm_risk_objective_category_view.xml',
        'views/erm_risk_objective_view.xml',
        'views/erm_risk_treatment_type_view.xml',
        'views/erm_risk_template_view.xml',
        'views/erm_risk_view.xml',
        'views/erm_risk_consequence_view.xml',
        'views/res_config_settings_views.xml',
        'data/erm_risk_impact_data.xml',
        'data/erm_risk_likelihood_data.xml',
        'data/erm_risk_velocity_data.xml',
        'data/erm_risk_consequence_data.xml',
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_backend": [
            "erm/static/src/css/custom.css",
            "erm/static/src/views/kanban/erm_custom_kanban_header.xml",
            "erm/static/src/js/erm_custom_kanban_header.js",
        ],
    },
    # 'post_init_hook': 'post_init_hook',
}