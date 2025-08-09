from odoo import models, fields, api


class ResCountryPostalCodeRules(models.Model):
    _name = "res.country.postal.code.rules"
    _description = "Country Postal Code Validation Rules"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    country_id = fields.Many2one("res.country", string="Country", required=True)

    # New fields
    prefix_digits = fields.Integer(string="Prefix Number of Digits", required=True)
    prefix_allow_letters = fields.Boolean(
        string="Allow Letters in Prefix", default=False
    )
    suffix_digits = fields.Integer(string="Suffix Number of Digits", required=True)
    suffix_allow_letters = fields.Boolean(
        string="Allow Letters in Suffix", default=False
    )

    # Backward compatibility field
    digits = fields.Integer(
        string="Number of Digits (Deprecated)",
        compute="_compute_digits",
        inverse="_inverse_digits",
    )

    _sql_constraints = [
        (
            "country_company_uniq",
            "unique(country_id, company_id)",
            "Rules for this country already exist for this company!",
        ),
    ]

    @api.depends("prefix_digits")
    def _compute_digits(self):
        for record in self:
            record.digits = record.prefix_digits

    def _inverse_digits(self):
        for record in self:
            record.prefix_digits = record.digits


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    postal_code_rules_ids = fields.One2many(
        comodel_name="res.country.postal.code.rules",
        related="company_id.postal_code_rules_ids",
        string="Postal Code Rules",
        readonly=False,
    )

    def set_values(self):
        """
        Override to handle any additional processing when saving settings
        """
        super(ResConfigSettings, self).set_values()
        # Add any additional save logic here if needed

    @api.model
    def get_values(self):
        """
        Override to add custom loading logic if needed
        """
        res = super(ResConfigSettings, self).get_values()
        # Add any additional loading logic here if needed
        return res


class ResCompany(models.Model):
    _inherit = "res.company"

    postal_code_rules_ids = fields.One2many(
        "res.country.postal.code.rules", "company_id", string="Postal Code Rules"
    )
