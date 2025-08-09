{
  "name": "Sales Advance Payments",
  "version": "17.0.1.0",
  "summary": "Adds advance payments option in sales orders. Advance payments will be automatically applied to the sales order's customer invoice once created.",
  "description": """
    Sales Advance Payments
    ======================
    
    This module adds an advance payments option in sales orders. Advance payments will be automatically
    applied to the sales order's customer invoice once created.
    
    Learn more at: [Daric SaaS](https://daric-saas.ir)
  """,
  "category": "Accounting/Payment",
  "author": "TORAHOPER",
  "website": "https://torahoper.ir",
  "license": "OPL-1",
  "depends": [
    "account_payment_advance_mac5",
    "sale"
  ],
  "data": [
    "views/sale_order_views.xml"
  ],
  "installable": False,
  "application": False,
  "auto_install": False,
  "images": [
    "static/description/banner.gif"
  ],
  "price": 100.00,
  "currency": "EUR",
  "support": "mac5_odoo@outlook.com",
  "live_test_url": "https://youtu.be/ubbcSh2ovUE"
}
