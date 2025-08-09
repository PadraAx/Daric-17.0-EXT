# -*- coding: utf-8 -*-
{
    'name': "DTM Point Based",  # Module title
    'author': 'Daric',
    'website': 'https://daric-saas.ir',
    'summary': "DTM Point Based",  # Module subtitle phrase
    'description': """
    Business Requirement Analysis
    - Point Based"
    """,  # Supports reStructuredText(RST) format  ,'rowno_in_tree'
    "category": "Governance/Digital Transformation Management",
    'version': '1.0.0',
    'depends': ['requirement'],
    'data': [
        'views/requirement_business_domain_view.xml',
        'views/requirement_assignments_view.xml',
        'views/requirement_review_view.xml',
        'views/requirement_critical_level_view.xml',
        'views/requirement_requierment_view.xml'
    ],
    'installable': True,
}

