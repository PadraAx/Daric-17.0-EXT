# models/res_city.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.mail.models.mail_thread import MailThread
from odoo.addons.mail.models.mail_activity_mixin import MailActivityMixin


class City(models.Model, MailThread, MailActivityMixin):
    """Model representing cities with hierarchical identification system.

    Cities belong to counties and maintain hierarchical IDs in the format:
    [CountryCode]-[State(2)County(2)Type(1)Seq(2)Reserved(3)]
    Example: 'IR-1001102000' where:
    - IR = Country Code
    - 10 = State Code
    - 01 = County Code
    - 1 = City Type Marker
    - 02 = City Sequence (01-99)
    - 000 = Reserved Digits
    """

    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _inherit = "res.city"
    _name = "res.city"
    _description = "City"
    _order = "hierarchical_id"
    _rec_names_search = ["name"]

    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # Descriptive Fields
    # ============================================
    description = fields.Html(
        string="Description",
        sanitize=True,
        sanitize_attributes=True,
        sanitize_form=True,
        strip_style=True,
        tracking=True,
        prefetch=False,
        help="Detailed description of the city",
    )
    is_county_capital = fields.Boolean(
        string="County Capital",
        tracking=True,
        help="Designates if this city is the capital of its county",
    )
    is_country_capital = fields.Boolean(string="Country Capital", tracking=True)
    is_state_capital = fields.Boolean(string="State Capital", tracking=True)

    # ============================================
    # External Relational Fields
    # ============================================
    country_id = fields.Many2one("res.country", string="Country", required=True)
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        domain="[('country_id', '=', country_id)]",
        required=True,
    )
    county_id = fields.Many2one(
        "res.county",
        string="County",
        domain="[('state_id', '=', state_id)]",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    city_div_ids = fields.One2many("res.city.div", "city_id", string="City Divisions")

    # ============================================
    # Demographic & Statistics Fields
    # ============================================
    address_ids = fields.One2many("res.address", "city_id", string="Addresses")
    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        help="Total partners in this city (including city divisions)",
    )

    # ============================================
    # Identification Fields
    # ============================================

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        index=True,
        readonly=True,
        copy=False,
        help="Format: [CountryCode]-[State(2)County(2)Type(1)Seq(2)Reserved(3)]",
    )

    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = [
        (
            "hierarchical_id_required",
            "CHECK(hierarchical_id IS NOT NULL)",
            "Hierarchical ID is required!",
        ),
        (
            "county_capital_uniq",
            "EXCLUDE (county_id WITH =) WHERE (is_county_capital = True)",
            "Each county can have only one capital city!",
        ),
        (
            "state_capital_uniq",
            "EXCLUDE (state_id WITH =) WHERE (is_state_capital = True)",
            "Each state can have only one capital city!",
        ),
        (
            "country_capital_uniq",
            "EXCLUDE (country_id WITH =) WHERE (is_country_capital = True)",
            "Each country can have only one capital city!",
        ),
    ]

    # ==========================================================================
    # Constraint Methods
    # ==========================================================================
    @api.constrains("county_id", "state_id")
    def _check_county_state(self):
        """Ensure the selected county belongs to the city's state."""
        for city in self:
            if city.county_id and city.county_id.state_id != city.state_id:
                raise ValidationError(
                    _("Selected county must belong to the city's state (%s)")
                    % city.state_id.name
                )

    @api.constrains("hierarchical_id")
    def _check_hierarchical_id(self):
        """Validate 12-character dash-free hierarchical ID."""
        for city in self:
            hid = city.hierarchical_id
            if hid and (len(hid) != 12 or not hid.isalnum()):
                raise ValidationError(
                    _("Invalid hierarchical ID format. Expected: CCSSccNN0000")
                )

    # ==========================================================================
    # Compute Methods
    # ==========================================================================
    @api.depends("address_ids.partner_count")
    def _compute_partner_count(self):
        """Calculate total partners in this city."""
        for city in self:
            city.partner_count = sum(city.address_ids.mapped("partner_count"))

    # ==========================================================================
    # CRUD Methods
    # ==========================================================================
    def name_get(self):
        """Display name representation for city records.

        Returns:
            - Simple name for Many2one dropdowns (when m2o_dropdown in context)
            - Full hierarchical path for other cases
        """
        if self._context.get("m2o_dropdown"):
            return [(rec.id, rec.name) for rec in self]
        return [(rec.id, rec.name) for rec in self]

    # @api.model_create_multi
    # def create(self, vals_list):
    #     new_vals_list = []

    #     # Preload all county records we'll need
    #     county_ids = {
    #         vals.get("county_id") for vals in vals_list if vals.get("county_id")
    #     }
    #     counties = (
    #         self.env["res.county"]
    #         .browse(county_ids)
    #         .read(["hierarchical_id", "country_id"])
    #     )
    #     county_map = {c["id"]: c for c in counties}

    #     # Group by county for sequence calculation
    #     county_city_map = {}
    #     for vals in vals_list:
    #         county_id = vals.get("county_id")
    #         if not county_id or county_id not in county_map:
    #             raise ValidationError(_("Missing or invalid county reference."))

    #         county_data = county_map[county_id]
    #         hierarchical_id = county_data["hierarchical_id"]
    #         country = self.env["res.country"].browse(county_data["country_id"][0])

    #         if not hierarchical_id or not country or not country.code:
    #             raise ValidationError(
    #                 _("County is missing required hierarchical info.")
    #             )

    #         county_code = hierarchical_id.split("-")[1][:4]  # state+county

    #         # Prepare map to count per-county sequence
    #         if county_id not in county_city_map:
    #             # Lock county to avoid race
    #             self.env.cr.execute(
    #                 "SELECT 1 FROM res_county WHERE id = %s FOR UPDATE", (county_id,)
    #             )
    #             self.env.cr.execute(
    #                 """
    #                 SELECT MAX(CAST(SUBSTRING(hierarchical_id, 8, 2) AS INTEGER))
    #                 FROM res_city
    #                 WHERE county_id = %s
    #                 AND hierarchical_id LIKE %s
    #                 AND hierarchical_id NOT LIKE 'TEMP%%'
    #             """,
    #                 (county_id, f"{country.code}-{county_code}1%"),
    #             )
    #             max_seq = self.env.cr.fetchone()[0] or 0
    #             county_city_map[county_id] = {"next_seq": max_seq + 1}

    #         # Assign sequential hierarchical_id directly
    #         seq = county_city_map[county_id]["next_seq"]
    #         if seq > 99:
    #             raise ValidationError(_("Maximum cities (99) reached for county."))

    #         new_hid = f"{country.code}-{county_code}1{seq:02d}000"
    #         vals["hierarchical_id"] = new_hid
    #         county_city_map[county_id]["next_seq"] += 1

    #         new_vals_list.append(vals)

    #     return super().create(new_vals_list)
    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []

        county_ids = {
            vals.get("county_id") for vals in vals_list if vals.get("county_id")
        }
        counties = (
            self.env["res.county"]
            .browse(county_ids)
            .read(["hierarchical_id", "country_id"])
        )
        county_map = {c["id"]: c for c in counties}
        county_seq_map = {}

        for vals in vals_list:
            county_id = vals.get("county_id")
            if not county_id or county_id not in county_map:
                raise ValidationError(_("Missing or invalid county reference."))

            county_data = county_map[county_id]
            county_hid = county_data["hierarchical_id"]
            country = self.env["res.country"].browse(county_data["country_id"][0])

            # county_hid must be exactly 12 chars: CCSScc000000
            if (
                not county_hid
                or len(county_hid) != 12
                or not county_hid.startswith(country.code)
            ):
                raise ValidationError(
                    _("County hierarchical ID format is invalid: %s") % county_hid
                )

            # Extract CCSScc (first 6 chars)
            prefix = county_hid[:6]

            if county_id not in county_seq_map:
                self.env.cr.execute(
                    "SELECT 1 FROM res_county WHERE id = %s FOR UPDATE", (county_id,)
                )
                self.env.cr.execute(
                    """
                    SELECT MAX(CAST(SUBSTRING(hierarchical_id, 8, 2) AS INTEGER))
                    FROM res_city
                    WHERE county_id = %s
                    AND hierarchical_id LIKE %s
                    AND hierarchical_id NOT LIKE 'TEMP%%'
                    """,
                    (county_id, f"{prefix}1%"),
                )
                max_seq = self.env.cr.fetchone()[0] or 0
                county_seq_map[county_id] = max_seq + 1

            seq = county_seq_map[county_id]
            if seq > 99:
                raise ValidationError(_("Maximum cities (99) reached for county."))

            # City format: CCSScc1NN000
            vals["hierarchical_id"] = f"{prefix}1{seq:02d}000"
            county_seq_map[county_id] += 1
            new_vals_list.append(vals)

        return super().create(new_vals_list)

    def write(self, vals):
        """Handle capital flag changes with recursion protection"""
        # Prevent recursion when updating capital flags
        if self.env.context.get("updating_capital"):
            return super().write(vals)

        res = super().write(vals)

        # Handle country capital changes
        if "is_country_capital" in vals:
            for city in self:
                country = city.country_id
                if vals["is_country_capital"]:
                    # Clear previous country capital
                    self.with_context(updating_capital=True).search(
                        [
                            ("country_id", "=", country.id),
                            ("is_country_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_country_capital": False})
                    country.with_context(updating_capital=True).write(
                        {"capital_id": city.id}
                    )
                elif country.capital_id == city:
                    country.with_context(updating_capital=True).write(
                        {"capital_id": False}
                    )

        # Handle state capital changes
        if "is_state_capital" in vals:
            for city in self:
                state = city.state_id
                if vals["is_state_capital"]:
                    # Clear previous state capital
                    self.with_context(updating_capital=True).search(
                        [
                            ("state_id", "=", state.id),
                            ("is_state_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_state_capital": False})
                    state.with_context(updating_capital=True).write(
                        {"capital_id": city.id}
                    )
                elif state.capital_id == city:
                    state.with_context(updating_capital=True).write(
                        {"capital_id": False}
                    )

        # Handle county capital changes
        if "is_county_capital" in vals and "res.county" in self.env:
            for city in self:
                county = city.county_id
                if vals["is_county_capital"]:
                    # Clear previous county capital
                    self.with_context(updating_capital=True).search(
                        [
                            ("county_id", "=", county.id),
                            ("is_county_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_county_capital": False})
                    county.with_context(updating_capital=True).write(
                        {"capital_id": city.id}
                    )
                elif county.capital_id == city:
                    county.with_context(updating_capital=True).write(
                        {"capital_id": False}
                    )

        return res

    # ==========================================================================
    # Business Logic Methods
    # ==========================================================================
    def _validate_capitals(self, cities):
        """Validate capital city uniqueness for created/updated cities."""
        for city in cities:
            if city.is_country_capital:
                existing = self.search(
                    [
                        ("country_id", "=", city.country_id.id),
                        ("is_country_capital", "=", True),
                        ("id", "!=", city.id),
                    ]
                )
                if existing:
                    raise ValidationError(_("This country already has a capital city"))

            if city.is_state_capital:
                existing = self.search(
                    [
                        ("state_id", "=", city.state_id.id),
                        ("is_state_capital", "=", True),
                        ("id", "!=", city.id),
                    ]
                )
                if existing:
                    raise ValidationError(_("This state already has a capital city"))

            if city.is_county_capital:
                existing = self.search(
                    [
                        ("county_id", "=", city.county_id.id),
                        ("is_county_capital", "=", True),
                        ("id", "!=", city.id),
                    ]
                )
                if existing:
                    raise ValidationError(_("This county already has a capital city"))

    def _update_capitals(self, vals):
        """Update capital references in parent country/state/county records.

        Args:
            vals (dict): Dictionary containing capital flag changes
        """
        # Handle country capital changes
        if "is_country_capital" in vals:
            for city in self:
                country = city.country_id
                if vals["is_country_capital"]:
                    # Clear previous country capital
                    self.search(
                        [
                            ("country_id", "=", country.id),
                            ("is_country_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_country_capital": False})
                    country.capital_id = city
                elif country.capital_id == city:
                    country.capital_id = False

        # Handle state capital changes
        if "is_state_capital" in vals:
            for city in self:
                state = city.state_id
                if vals["is_state_capital"]:
                    # Clear previous state capital
                    self.search(
                        [
                            ("state_id", "=", state.id),
                            ("is_state_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_state_capital": False})
                    state.capital_id = city
                elif state.capital_id == city:
                    state.capital_id = False

        # Handle county capital changes
        if "is_county_capital" in vals:
            for city in self:
                county = city.county_id
                if vals["is_county_capital"]:
                    # Clear previous county capital
                    self.search(
                        [
                            ("county_id", "=", county.id),
                            ("is_county_capital", "=", True),
                            ("id", "!=", city.id),
                        ]
                    ).write({"is_county_capital": False})
                    county.capital_id = city
                elif county.capital_id == city:
                    county.capital_id = False
