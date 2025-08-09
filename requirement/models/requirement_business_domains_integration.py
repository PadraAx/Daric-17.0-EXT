from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class RequirementBusinessDomainsIntegration(models.Model):
    _name = "requirement.business.domains.integration"
    _description = "Business Domains Integration"

    parent_id = fields.Many2one('requirement.business.domains', string="Parent")
    integration_id = fields.Many2one('requirement.business.domains', string="Business Domain", domain="[('active', '=', True)]")
    icon_image = fields.Binary(string='Icon', related="integration_id.module_id.icon_image" , readonly=True)
    integration_type = fields.Selection(
        selection=[
            ("1", "Functional Integration"),
            ("2", "Intra-Module Inheritance"),
            ("3", "External Service Integration (API Integration)"),
            ("4", "Connector Modules"),
            ("5", "Reporting Integration"),
            ("6", " Third-Party App Integration"),
            ("7", "Website Integration"),
            ("8", "Middleware Integration"),
            ("9", "Custom API Development"),
            ("10", "IoT Integration"),
        ],
        string='Integration Typer',default="1" , help='''
                1. Functional Integration (Modules work together to provide extended functionality.)
                2. Intra-Module Inheritance(In Odoo, a module can extend the functionality of another module using inheritance. There are two types: Classical Inheritance, View Inheritance)
                3. External Service Integration (API Integration)
                Odoo integrates with external services via APIs. Common examples include: Payment Gateways (e.g., PayPal, Stripe). Shipping Providers (e.g., FedEx, UPS). External APIs (e.g., Google Maps for geo-location, social media for marketing).
                4. Connector Modules
                Connector modules are used to sync Odoo with external systems, including: E-commerce Platforms (e.g., Magento, WooCommerce, Shopify). CRM Systems (e.g., Salesforce). Marketplaces (e.g., Amazon, eBay).
                5. Reporting Integration
                Odoo integrates with various reporting tools for advanced reporting capabilities: Business Intelligence (BI) Tools (e.g., integrating Odoo with Power BI or Tableau).
                6. Third-Party App Integration
                Odoo has a marketplace with third-party apps that extend or integrate with core modules. These apps can be installed to add industry-specific functionality, improve usability, or introduce new features, like project management tools, fleet management, or POS systems.
                7. Website Integration
                Website & eCommerce: Odoo’s Website module integrates with CRM, Sales, Inventory, and Accounting for eCommerce.
                8. Middleware Integration
                Odoo can integrate with middleware systems that serve as an intermediary for connecting multiple software applications (like ERP, CRM, or databases), ensuring smooth data exchange.
                9. Custom API Development
                Odoo provides an XML-RPC API and JSON-RPC API for creating custom integrations to connect with third-party applications. Developers can build custom connectors to link Odoo with non-standard systems.
                10. IoT Integration
                Odoo integrates with IoT (Internet of Things) devices. For example: Point of Sale (POS) systems integrate with barcode scanners, printers, or scales.
        ''')
    
#   1. Functional Integration
#                 Modules work together to provide extended functionality. For example:

#                 Sales integrates with Inventory to update stock levels after a sale.
#                 Accounting integrates with Sales, Purchases, and HR for automatic invoicing, expense management, and payroll processing.
#                 2. Intra-Module Inheritance
#                 In Odoo, a module can extend the functionality of another module using inheritance. There are two types:

#                 Classical Inheritance: Extending models to add new fields or methods, often used to enhance functionality of another module (e.g., extending the sale.order model from the Sales module).
#                 View Inheritance: Altering or adding to an existing view from another module, without modifying the original view file.
#                 3. External Service Integration (API Integration)
#                 Odoo integrates with external services via APIs. Common examples include:

#                 Payment Gateways (e.g., PayPal, Stripe).
#                 Shipping Providers (e.g., FedEx, UPS).
#                 External APIs (e.g., Google Maps for geo-location, social media for marketing).
#                 4. Connector Modules
#                 Connector modules are used to sync Odoo with external systems, including:

#                 E-commerce Platforms (e.g., Magento, WooCommerce, Shopify).
#                 CRM Systems (e.g., Salesforce).
#                 Marketplaces (e.g., Amazon, eBay).
#                 5. Reporting Integration
#                 Odoo integrates with various reporting tools for advanced reporting capabilities:

#                 Business Intelligence (BI) Tools (e.g., integrating Odoo with Power BI or Tableau).
#                 Odoo Studio: Allows for custom reports and dashboards within Odoo.
#                 6. Third-Party App Integration
#                 Odoo has a marketplace with third-party apps that extend or integrate with core modules. These apps can be installed to add industry-specific functionality, improve usability, or introduce new features, like project management tools, fleet management, or POS systems.

#                 7. Website Integration
#                 Website & eCommerce: Odoo’s Website module integrates with CRM, Sales, Inventory, and Accounting for eCommerce.
#                 Website Form Integration: Website forms integrate with backend apps (e.g., Lead Generation from contact forms into the CRM module).
#                 8. Middleware Integration
#                 Odoo can integrate with middleware systems that serve as an intermediary for connecting multiple software applications (like ERP, CRM, or databases), ensuring smooth data exchange.

#                 9. Custom API Development
#                 Odoo provides an XML-RPC API and JSON-RPC API for creating custom integrations to connect with third-party applications. Developers can build custom connectors to link Odoo with non-standard systems.

#                 10. IoT Integration
#                 Odoo integrates with IoT (Internet of Things) devices. For example:

#                 Point of Sale (POS) systems integrate with barcode scanners, printers, or scales.
#                 Manufacturing integrates with machines or sensors for automated data collection.
#                 These types of integration enhance Odoo's ability to work as a complete business management suite, connecting multiple facets of an organization



