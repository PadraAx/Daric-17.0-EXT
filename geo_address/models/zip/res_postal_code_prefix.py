from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResPostalCodePrefix(models.Model):
    _name = "res.postal.code.prefix"
    _description = "Postal Code Prefix"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "postal_code_prefix"

    # Fields
    postal_code_prefix = fields.Char(
        string="Postal Code Prefix",
        required=True,
        help="Postal code prefix (format depends on country)",
    )
    address_ids = fields.One2many(
        "res.address", "postal_code_prefix_id", string="Addresses"
    )

    # Location fields (synced from addresses)
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2one(
        "res.country.state", string="State", domain="[('country_id', '=', country_id)]"
    )
    county_id = fields.Many2one(
        "res.county", string="County", domain="[('state_id', '=', state_id)]"
    )
    city_id = fields.Many2one(
        "res.city", string="City", domain="[('county_id', '=', county_id)]"
    )
    city_div_id = fields.Many2one(
        "res.city.div", string="City Division", domain="[('city_id', '=', city_id)]"
    )
    rural_dist_id = fields.Many2one(
        "res.rural.dist",
        string="Rural District",
        domain="[('county_id', '=', county_id)]",
    )
    rural_dist_div_id = fields.Many2one(
        "res.rural.dist.div",
        string="Rural District Division",
        domain="[('rural_dist_id', '=', rural_dist_id)]",
    )
    address_count = fields.Integer(
        string="Address Count",
        compute="_compute_address_count",
        store=True,
    )

    # Constraints - Removed the hardcoded format constraint
    _sql_constraints = [
        (
            "prefix_unique",
            "UNIQUE(postal_code_prefix)",
            "Postal code prefix must be unique!",
        ),
    ]

    @api.depends("address_ids")
    def _compute_address_count(self):
        for record in self:
            record.address_count = len(record.address_ids)

    @api.constrains("postal_code_prefix", "country_id")
    def _check_prefix_format(self):
        for record in self:
            if not record.country_id:
                continue  # Skip validation if no country is set

            # Get the validation rules for the country
            rules = self.env["res.country.postal.code.rules"].search(
                [("country_id", "=", record.country_id.id)], limit=1
            )

            if not rules:
                continue  # No rules defined for this country

            # Build the regex pattern based on rules
            pattern = "^"
            if rules.prefix_allow_letters:
                pattern += "[A-Za-z0-9]"
            else:
                pattern += "[0-9]"
            pattern += f"{{{rules.digits}}}$"

            if not re.match(pattern, record.postal_code_prefix):
                raise ValidationError(
                    _(
                        "Postal Code Prefix for %(country)s must be %(digits)d %(type)s characters!"
                    )
                    % {
                        "country": record.country_id.name,
                        "digits": rules.prefix_digits,
                        "type": (
                            _("alphanumeric")
                            if rules.prefix_allow_letters
                            else _("numeric")
                        ),
                    }
                )

    def get_country_rules(self, country_id):
        """Helper method to get rules for a specific country"""
        return self.env["res.country.postal.code.rules"].search(
            [("country_id", "=", country_id)], limit=1
        )
