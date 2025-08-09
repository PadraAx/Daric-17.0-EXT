{
    'name': 'just workflow bpmn',
    'category': 'Governance/Business Proccesses Management',
    'summary': """
        Odoo bpmn Web Diagram by just.
    """,
    'author': 'Daric',
    'website': "https://daric-saas.ir",
    'license': 'LGPL-3',
    'version': '17.0.10.1',
    'depends': [
        'web'
    ],
    'data': [
    ],

    'assets': {
        'web.assets_backend': [
            'just_workflow_bpmn/static/lib/js/bpmn.min.js',
            'just_workflow_bpmn/static/lib/scss/bpmn-js.css',
            'just_workflow_bpmn/static/lib/scss/diagram-js.css',
            'just_workflow_bpmn/static/lib/scss/bpmn.css',
            'just_workflow_bpmn/static/src/js/diagram_controller.js',
            'just_workflow_bpmn/static/src/js/diagram_view.js',
            'just_workflow_bpmn/static/src/scss/diagram_view.scss',   
            'just_workflow_bpmn/static/src/js/flowlogs.js',
	        'just_workflow_bpmn/static/src/xml/*.xml',
        ],
    },

    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    "price": 4000.0,
    "currency": "USD",
}
