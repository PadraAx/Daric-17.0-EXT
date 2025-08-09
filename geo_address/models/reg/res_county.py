import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class County(models.Model):
    _name = "res.county"
    _description = "County"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "country_id, state_id, name"
    _rec_name = "name"

    # ================ Fields ================
    name = fields.Char(
        string="County Name", required=True, translate=True, tracking=True
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        required=True,
        domain="[('country_id', '=', country_id)]",
        ondelete="restrict",
        tracking=True,
    )
    hrchy_id = fields.Many2one(
        "hrchy.id",
        string="Hierarchy Reference",
        compute="_compute_hrchy_id",
        store=True,
        index=True,
    )

    def _compute_hrchy_id(self):
        for country in self:
            hrchy_record = self.env["hrchy.id"].search(
                [
                    ("country_id", "=", country.id),
                    ("state_id", "=", False),
                    ("county_id", "=", False),
                    ("city_id", "=", False),
                    ("rural_id", "=", False),
                ],
                limit=1,
            )
            country.hrchy_id = hrchy_record

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        required=True,
        index=True,
        readonly=True,
        help="Format: [CountryCode]-[SystemID] (e.g., IR-1001000000)",
        copy=False,
    )
    capital_id = fields.Many2one(
        "res.city",
        string="County Capital",
        domain="[('state_id', '=', state_id), ('country_id', '=', country_id)]",
        help="The capital city of this county",
        ondelete="set null",
        tracking=True,
    )
    capital_name = fields.Char(
        string="Capital Name", related="capital_id.name", store=True, readonly=True
    )
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=True,
        prefetch=False,
        help="Detailed description of the county",
    )
    city_ids = fields.One2many("res.city", "county_id", string="Cities")
    rural_dist_ids = fields.One2many(
        "res.rural.dist", "county_id", string="Rural Districts"
    )
    address_ids = fields.One2many("res.address", "county_id", string="Addresses")
    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        help="Total partners in this county",
    )

    # ================ SQL Constraints ================
    _sql_constraints = [
        (
            "hierarchical_id_uniq",
            "UNIQUE(hierarchical_id)",
            "Hierarchical ID must be unique!",
        ),
        (
            "capital_in_county_check",
            "CHECK (capital_id IS NULL OR capital_id.county_id = id)",
            "The capital city must belong to this county!",
        ),
        (
            "capital_state_consistency_check",
            "CHECK (capital_id IS NULL OR capital_id.state_id = state_id)",
            "The capital city must belong to the same state as the county!",
        ),
        (
            "capital_country_consistency_check",
            "CHECK (capital_id IS NULL OR capital_id.country_id = country_id)",
            "The capital city must belong to the same country as the county!",
        ),
        (
            "state_country_consistency",
            "CHECK (state_id IS NULL OR state_id.country_id = country_id)",
            "The state must belong to the selected country!",
        ),
    ]

    # ================ Compute Methods ================
    @api.depends("address_ids.partner_count")
    def _compute_partner_count(self):
        for county in self:
            county.partner_count = sum(county.address_ids.mapped("partner_count"))

    # ================ CRUD Methods ================
    # @api.model_create_multi
    # def create(self, vals_list):
    #     counties_to_create = []
    #     next_numbers = {}  # Track next_number per state.id

    #     for vals in vals_list:
    #         country = self.env["res.country"].browse(vals.get("country_id"))
    #         state = self.env["res.country.state"].browse(vals.get("state_id"))

    #         if not country.exists() or not country.code:
    #             raise ValidationError(
    #                 _("Country is missing or doesn't have a country code.")
    #             )
    #         if not state.exists() or not state.hierarchical_id:
    #             raise ValidationError(
    #                 _("State is missing or doesn't have a hierarchical ID.")
    #             )
    #         if state.country_id != country:
    #             raise ValidationError(
    #                 _("The selected state doesn't belong to the selected country.")
    #             )

    #         # Advisory lock to avoid cross-session conflicts
    #         self.env.cr.execute("SELECT pg_advisory_xact_lock(%s)", (state.id,))

    #         state_code_full = state.hierarchical_id.split("-")[1]
    #         state_id = state.id

    #         if state_id not in next_numbers:
    #             # Only query the DB once per state
    #             last_county = self.search(
    #                 [("state_id", "=", state_id)], order="hierarchical_id DESC", limit=1
    #             )
    #             if last_county and last_county.hierarchical_id:
    #                 last_code = last_county.hierarchical_id.split("-")[1]
    #                 last_number = int(last_code[2:4])  # County sequence
    #             else:
    #                 last_number = 0
    #             next_numbers[state_id] = last_number + 1
    #         else:
    #             next_numbers[state_id] += 1

    #         if next_numbers[state_id] > 99:
    #             raise ValidationError(
    #                 _("Maximum number of counties (99) reached for state: %s")
    #                 % state.name
    #             )

    #         new_numeric_code = (
    #             state_code_full[:2]
    #             + f"{next_numbers[state_id]:02d}"
    #             + state_code_full[4:]
    #         )

    #         vals["hierarchical_id"] = f"{country.code}-{new_numeric_code}"
    #         counties_to_create.append(vals)

    #     return super().create(counties_to_create)

    @api.model_create_multi
    def create(self, vals_list):
        counties_to_create = []
        next_numbers = {}  # per state.id

        for vals in vals_list:
            country = self.env["res.country"].browse(vals.get("country_id"))
            state = self.env["res.country.state"].browse(vals.get("state_id"))

            # Basic validations
            if not country.exists() or not country.code:
                raise ValidationError(
                    _("Country is missing or doesn't have a country code.")
                )
            if not state.exists() or not state.hierarchical_id:
                raise ValidationError(
                    _("State is missing or doesn't have a hierarchical ID.")
                )
            if state.country_id != country:
                raise ValidationError(
                    _("The selected state doesn't belong to the selected country.")
                )

            self.env.cr.execute("SELECT pg_advisory_xact_lock(%s)", (state.id,))

            # state hierarchical_id format: CCNN00000000  (country code + 2-digit seq + 8 zeros)
            hier_id = state.hierarchical_id
            if len(hier_id) != 12 or not hier_id[:2] == country.code:
                raise ValidationError(
                    _("State hierarchical ID format is invalid: %s") % hier_id
                )

            state_seq = hier_id[2:4]  # the two digits after country code
            if not state_seq.isdigit():
                raise ValidationError(
                    _("State hierarchical ID format is invalid: %s") % hier_id
                )

            state_id = state.id

            # next county sequence number (01-99)
            if state_id not in next_numbers:
                last_county = self.search(
                    [("state_id", "=", state_id)], order="hierarchical_id DESC", limit=1
                )
                if last_county and last_county.hierarchical_id:
                    # county id: CCNNCC000000  (country 2 + state 2 + county 2 + 6 zeros)
                    cnty_part = last_county.hierarchical_id[4:6]
                    last_num = int(cnty_part) if cnty_part.isdigit() else 0
                else:
                    last_num = 0
                next_numbers[state_id] = last_num + 1
            else:
                next_numbers[state_id] += 1

            if next_numbers[state_id] > 99:
                raise ValidationError(
                    _("Maximum number of counties (99) reached for state: %s")
                    % state.name
                )

            # Build county hierarchical_id: CC + SS + CC + 000000
            county_seq = f"{next_numbers[state_id]:02d}"
            vals["hierarchical_id"] = f"{country.code}{state_seq}{county_seq}".ljust(
                12, "0"
            )
            counties_to_create.append(vals)

        return super().create(counties_to_create)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     counties = []
    #     for vals in vals_list:
    #         country = self.env["res.country"].browse(vals.get("country_id"))
    #         state = self.env["res.country.state"].browse(vals.get("state_id"))

    #         if not country or not country.code:
    #             raise ValidationError(
    #                 _("Country is missing or doesn't have a country code.")
    #             )
    #         if not state or not state.hierarchical_id:
    #             raise ValidationError(
    #                 _("State is missing or doesn't have a hierarchical ID.")
    #             )
    #         if state.country_id != country:
    #             raise ValidationError(
    #                 _("The selected state doesn't belong to the selected country.")
    #             )

    #         # Lock the parent state to avoid race conditions
    #         self.env.cr.execute(
    #             "SELECT 1 FROM res_country_state WHERE id = %s FOR UPDATE", (state.id,)
    #         )

    #         # Extract numeric part from state's hierarchical_id
    #         try:
    #             state_code_full = state.hierarchical_id.split("-")[1]
    #         except IndexError:
    #             raise ValidationError(
    #                 _("Invalid state hierarchical ID format: %s")
    #                 % state.hierarchical_id
    #             )

    #         # Search for the max county number within the same state
    #         existing = self.search(
    #             [("state_id", "=", state.id)], order="hierarchical_id DESC", limit=1
    #         )

    #         if existing and existing.hierarchical_id:
    #             last_id = existing.hierarchical_id.split("-")[1]
    #             last_number = int(last_id[2:4])  # Extract county sequence
    #             next_number = last_number + 1
    #         else:
    #             next_number = 1

    #         if next_number > 99:
    #             raise ValidationError(
    #                 _("Maximum number of counties (99) reached for state: %s")
    #                 % state.name
    #             )

    #         # Compose the new 10-digit code
    #         new_numeric_code = (
    #             state_code_full[:2] + f"{next_number:02d}" + state_code_full[4:]
    #         )

    #         # Final hierarchical ID
    #         vals["hierarchical_id"] = f"{country.code}-{new_numeric_code}"
    #         counties.append(vals)

    #     return super().create(counties)

    def write(self, vals):
        # Handle capital update with recursion protection
        if "capital_id" in vals:
            capital_id = vals.get("capital_id")
            for county in self:
                if not capital_id:
                    # Clear existing capital flags
                    self.env["res.city"].with_context(updating_capital=True).search(
                        [
                            ("county_id", "=", county.id),
                            ("is_county_capital", "=", True),
                        ]
                    ).write({"is_county_capital": False})
                else:
                    # Clear old capitals
                    old_capitals = (
                        self.env["res.city"]
                        .with_context(updating_capital=True)
                        .search(
                            [
                                ("county_id", "=", county.id),
                                ("is_county_capital", "=", True),
                                ("id", "!=", capital_id),
                            ]
                        )
                    )
                    old_capitals.write({"is_county_capital": False})

                    # Set new capital
                    new_capital = self.env["res.city"].browse(capital_id)
                    if new_capital:
                        new_capital.with_context(updating_capital=True).write(
                            {
                                "is_county_capital": True,
                                "county_id": county.id,
                                "state_id": county.state_id.id,
                                "country_id": county.country_id.id,
                            }
                        )

        return super().write(vals)

    # ================ Onchange Methods ================
    @api.onchange("country_id")
    def _onchange_country_id(self):
        """Update domain filters when country changes"""
        if self.country_id:
            return {
                "domain": {
                    "state_id": [("country_id", "=", self.country_id.id)],
                    "capital_id": [("country_id", "=", self.country_id.id)],
                },
                "value": {"state_id": False, "capital_id": False},
            }
        return {}

    @api.onchange("state_id")
    def _onchange_state_id(self):
        """Update domain filters when state changes"""
        if self.state_id:
            return {
                "domain": {
                    "capital_id": [
                        ("state_id", "=", self.state_id.id),
                        ("country_id", "=", self.country_id.id),
                    ]
                },
                "value": {"capital_id": False},
            }
        return {}

    @api.onchange("capital_id")
    def _onchange_capital_id(self):
        """Sync capital_id changes with city flags"""
        if not self.capital_id:
            # Clear all county capital flags if unsetting capital
            self.env["res.city"].search(
                [("county_id", "=", self.id), ("is_county_capital", "=", True)]
            ).write({"is_county_capital": False})
        else:
            # Ensure the city is marked as capital
            if not self.capital_id.is_county_capital:
                self.capital_id.write(
                    {
                        "is_county_capital": True,
                        "county_id": self.id,
                        "state_id": self.state_id.id,
                        "country_id": self.country_id.id,
                    }
                )
            # Clear any other cities marked as capital
            self.env["res.city"].search(
                [
                    ("county_id", "=", self.id),
                    ("is_county_capital", "=", True),
                    ("id", "!=", self.capital_id.id),
                ]
            ).write({"is_county_capital": False})

    # ================ Action Methods ================
    def open_capital_city(self):
        """Open the capital city form view"""
        self.ensure_one()
        if not self.capital_id:
            raise ValidationError(_("This county has no capital city assigned"))
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.city",
            "view_mode": "form",
            "res_id": self.capital_id.id,
            "target": "current",
            "context": {
                "create": False,
                "edit": True,
                "form_view_initial_mode": "edit",
            },
        }
