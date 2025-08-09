{
  "name": "Chart of Account Hierarchy",
  "summary": "Adds parent account functionality and enables a hierarchical chart of accounts view with advanced reporting options.",
  "category": "Accounting/Account Charts",
  "version": "17.0.1.1.1",
  "sequence": 1,
  "author": "TORAHOPER",
  "license": "OPL-1",
  "website": "https://torahoper.ir",
  "description": """
    The Parent Account module introduces advanced features to enhance accounting in Odoo:
    - Adds a new account type 'View' for better hierarchy.
    - Includes parent accounts for clear chart of accounts organization.
    - Displays a hierarchical view of the chart of accounts.
    - Provides credit, debit, and balance calculations per account.
    - Enables filtering the chart of accounts by date and target moves.
    - Includes PDF and XLS export options for financial reporting.

    To access the chart of account hierarchy, activate the group setting: "Show chart of account structure."

    Learn more at: [Daric SaaS](https://daric-saas.ir)
  """,
  "depends": [
    "account"
  ],
  "data": [
    "security/account_parent_security.xml",
    "security/ir.model.access.csv",
    "views/account_view.xml",
    "views/open_chart.xml",
    "views/report_coa_hierarchy.xml",
    "views/res_config_view.xml"
  ],
  "assets": {
    "web.assets_common": [
      "account_parent/static/src/scss/coa_hierarchy.scss"
    ],
    "web.assets_backend": [
      "account_parent/static/src/js/account_parent_backend.js",
      "account_parent/static/src/js/account_type_selection.js",
      "account_parent/static/src/xml/account_parent_backend.xml",
      "account_parent/static/src/xml/account_parent_line.xml"
    ]
  },
  "images": [
    "static/description/account_parent_9.png"
  ],
  "application": True,
  "installable": True,
  "auto_install": False,
  "post_init_hook": "_assign_account_parent"
}
