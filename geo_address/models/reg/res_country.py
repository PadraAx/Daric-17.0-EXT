from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.mail.models.mail_thread import MailThread
from odoo.addons.mail.models.mail_activity_mixin import MailActivityMixin


class Country(models.Model, MailThread, MailActivityMixin):
    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _inherit = "res.country"
    _name = "res.country"
    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # RELATIONAL FIELDS
    # ============================================
    capital_id = fields.Many2one(
        "res.city",
        string="Capital City",
        help="The capital city of this country",
        tracking=True,
        ondelete="set null",
    )
    address_ids = fields.One2many(
        "res.address",
        "country_id",
        string="Addresses",
        tracking=True,
        help="All addresses associated with this country",
    )

    # ============================================
    # COMPUTED FIELDS
    # ============================================
    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        tracking=True,
        help="Total partners in this country",
    )
    # ============================================
    # TEXT / CONTENT FIELDS
    # ============================================
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=True,
        tracking=True,
        prefetch=False,
        help="Detailed description of the country",
    )
    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = [
        (
            "capital_in_country_check",
            "CHECK (capital_id IS NULL OR capital_id.country_id = id)",
            "The capital city must belong to this country!",
        ),
    ]

    # ==========================================================================
    # COMPUTE METHODS
    # ==========================================================================
    @api.depends("address_ids.partner_count")
    def _compute_partner_count(self):
        for country in self:
            country.partner_count = sum(country.address_ids.mapped("partner_count"))

    # ==========================================================================
    # ONCHANGE METHODS
    # ==========================================================================
    @api.onchange("capital_id")
    def _onchange_capital_id(self):
        """Sync capital_id changes with city flags"""
        if not self.capital_id:
            self.env["res.city"].search(
                [("country_id", "=", self.id), ("is_country_capital", "=", True)]
            ).write({"is_country_capital": False})
        else:
            if not self.capital_id.is_country_capital:
                self.capital_id.write(
                    {
                        "is_country_capital": True,
                        "country_id": self.id,
                    }
                )
            self.env["res.city"].search(
                [
                    ("country_id", "=", self.id),
                    ("is_country_capital", "=", True),
                    ("id", "!=", self.capital_id.id),
                ]
            ).write({"is_country_capital": False})

    # ==========================================================================
    # OVERRIDE METHODS
    # ==========================================================================
    @api.model_create_multi
    def create(self, vals_list):
        countries = super().create(vals_list)
        try:
            # Bypass constraints temporarily
            with self.env.cr.savepoint():
                self.env["hrchy.id"].with_context(bypass_constraints=True).create(
                    [
                        {
                            "country_id": country.id,
                            "active": True,
                        }
                        for country in countries
                    ]
                )
        except Exception as e:
            _logger.error("HRCHY_ID CREATION FAILED: %s", str(e))
        return countries

    def write(self, vals):
        """Handle capital city changes during write operations"""
        if "capital_id" in vals:
            if not vals["capital_id"]:
                self.env["res.city"].search(
                    [("country_id", "in", self.ids), ("is_country_capital", "=", True)]
                ).write({"is_country_capital": False})
            else:
                old_capitals = self.env["res.city"].search(
                    [
                        ("country_id", "in", self.ids),
                        ("is_country_capital", "=", True),
                        ("id", "!=", vals["capital_id"]),
                    ]
                )
                old_capitals.write({"is_country_capital": False})

                new_capital = self.env["res.city"].browse(vals["capital_id"])
                if not new_capital.is_country_capital:
                    new_capital.write({"is_country_capital": True})

        return super().write(vals)

    # ==========================================================================
    # ACTION METHODS
    # ==========================================================================
    def open_capital_city(self):
        """Open the capital city form view"""
        self.ensure_one()
        capital_city = self.env["res.city"].search(
            [("country_id", "=", self.id), ("is_country_capital", "=", True)], limit=1
        )

        if not capital_city:
            raise ValidationError(_("This country has no capital city assigned."))

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.city",
            "view_mode": "form",
            "res_id": capital_city.id,
            "target": "current",
            "context": {
                "create": False,
                "edit": True,
                "form_view_initial_mode": "edit",
            },
        }
