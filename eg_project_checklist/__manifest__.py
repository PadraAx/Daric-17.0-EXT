{
    "name": "Project Checklist",

    'version': "17.0",

    'category': "Services/Project",

    "summary": "This app will display Custom checklist and their progress in percentage, according to marked checklist in Project",
    
    'author': "TORAHOPER",
    
    'website': "https://torahoper.ir",

    "depends": ['project'],
    
    "data": [
        "views/project_project_form.xml",
        "views/project_checklist_view.xml",
        "security/ir.model.access.csv"

    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
