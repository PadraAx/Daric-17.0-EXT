# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
import logging

_logger = logging.getLogger(__name__)


class ResAddress(models.Model):
    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _name = "res.address"
    _description = "Addresses (City or Rural District Division)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "hierarchical_id"
    _order = "hierarchical_id"

    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # Descriptive Fields
    # ============================================
    image_1024 = fields.Image("Cover Image", max_width=1024, max_height=768)
    image = fields.Image("Image")
    image_url = fields.Char("Image URL", compute="_compute_image_url")
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=True,
        prefetch=False,
        help="Detailed description of the address",
    )
    address_type = fields.Selection(
        selection=[
            ("city", "City Address"),
            ("rural_dist", "Rural District Address"),
        ],
        string="Address Type",
        required=True,
        default="city",
    )
    address_text = fields.Text(
        string="Postal Address",
        compute="_compute_address_text",
        store=True,
        help="Computed full textual address including hierarchy and postal code.",
    )
    active = fields.Boolean(string="Active", default=True)
    partner_ids = fields.One2many("res.partner", "address_id", string="Partners")
    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        help="Number of partners linked to this address",
    )

    # ============================================
    # Core Fields (Required for All Addresses)
    # ============================================
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        required=True,
        domain="[('country_id', '=', country_id)]",
    )
    county_id = fields.Many2one(
        "res.county",
        string="County",
        required=True,
        domain="[('state_id', '=', state_id)]",
    )
    postal_code_prefix_id = fields.Many2one(
        "res.postal.code.prefix", string="Postal Code Prefix", required=True
    )
    postal_code_suffix = fields.Char(string="Postal Code Suffix", required=True)
    postal_code = fields.Char(
        string="Postal Code", compute="_compute_postal_code", store=True
    )
    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        compute="_compute_hierarchical_id",
        store=True,
        readonly=True,
        index=True,
    )

    @api.depends("unit_id.hierarchical_id")
    def _compute_hierarchical_id(self):
        for rec in self:
            rec.hierarchical_id = rec.unit_id.hierarchical_id or False

    bldg_complex_name = fields.Char(
        string="Building Complex",
        compute="_compute_bldg_complex_name",
        store=True,
        help="Name of the building complex or community.",
    )

    bldg_id = fields.Many2one(
        "bldg.building",
        string="Building",
        compute="_compute_clear_bldg_id",
        readonly=False,
        store=True,
        domain="[('id','in',available_bldg_ids)]",
    )

    bldg_number = fields.Char(
        string="Building Number",
        related="bldg_id.name",
        store=True,
        readonly=True,
        help="Number or identifier of the building within the complex.",
    )
    available_bldg_ids = fields.Many2many(
        "bldg.building",
        store=True,
        compute="_compute_available_bldg_ids",
    )

    floor_id = fields.Many2one(
        "bldg.floor",
        string="Floor",
        store=True,
        domain="[('id', 'in', available_floor_ids)]",
        help="Floor number where the unit is located.",
    )
    available_floor_ids = fields.Many2many(
        "bldg.floor",
        string="Available Floors",
        compute="_compute_available_floor_ids",
        store=False,
    )
    unit_id = fields.Many2one(
        "bldg.unit",
        string="Unit / Apartment",
        store=True,
        domain="[('id', 'in', available_unit_ids)]",
        help="Specific unit or apartment number within the building.",
    )
    available_unit_ids = fields.Many2many(
        "bldg.unit",
        compute="_compute_available_unit_ids",
        store=False,
    )

    # ============================================
    # City-Specific Address Fields
    # ============================================
    city_id = fields.Many2one(
        "res.city",
        string="City",
        domain="[('county_id', '=', county_id)]",
    )
    city_div_id = fields.Many2one(
        "res.city.div",
        string="City Division",
        domain="[('city_id', '=', city_id)]",
    )

    # ============================================
    # Rural District-Specific Address Fields
    # ============================================
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

    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = [
        (
            "suffix_format",
            "CHECK(postal_code_suffix ~ '^[A-Za-z0-9]+$')",
            "Suffix must contain only alphanumeric characters!",
        ),
    ]

    # ==========================================================================
    # Methods
    # ==========================================================================
    # ============================================
    # Computed Fields
    # ============================================
    def _compute_image_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if rec.image_1024:
                rec.image_url = f"{base_url}/web/image/res.address/{rec.id}/image_1024"
            else:
                rec.image_url = f"{base_url}/web/static/img/placeholder.png"

    @api.depends("partner_ids")
    def _compute_partner_count(self):
        for rec in self:
            rec.partner_count = len(rec.partner_ids)

    @api.depends("postal_code_prefix_id.postal_code_prefix", "postal_code_suffix")
    def _compute_postal_code(self):
        for rec in self:
            if rec.postal_code_prefix_id and rec.postal_code_suffix:
                rec.postal_code = f"{rec.postal_code_prefix_id.postal_code_prefix}{rec.postal_code_suffix}"
            else:
                rec.postal_code = False

    def _geo_localize(self):
        if not self._context.get("force_geo_localize") and (
            self._context.get("import_file")
            or any(
                config.get(key)
                for key in ["test_enable", "test_file", "init", "update"]
            )
        ):
            return False

        addresses_not_geo_localized = self.env["res.address"]
        for rec in self.with_context(lang="en_US"):
            result = self._geo_localize(
                street=rec.bldg_id,
                zip=rec.postal_code,
                city=rec.city_id.name if rec.city_id else "",
                state=rec.state_id.name if rec.state_id else "",
                country=rec.country_id.name if rec.country_id else "",
            )

            if result:
                rec.write(
                    {
                        "latitude": result[0],
                        "longitude": result[1],
                        "date_localization": fields.Date.context_today(rec),
                    }
                )
            else:
                addresses_not_geo_localized |= rec

        if addresses_not_geo_localized:
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "simple_notification",
                {
                    "type": "danger",
                    "title": _("Warning"),
                    "message": _("No match found for the following address(es): %s")
                    % ", ".join(addresses_not_geo_localized.mapped("hierarchical_id")),
                },
            )
        return True

    @api.depends(
        "address_type",
        "country_id",
        "state_id",
        "county_id",
        "city_id",
        "city_div_id",
        "rural_dist_id",
        "rural_dist_div_id",
        "bldg_complex_name",
        "bldg_id",
        "floor_id",
        "unit_id",
        "postal_code",
    )
    def _compute_address_text(self):
        _logger.debug("Computing address text for %d records (inherited)", len(self))

        def get_full_path(record):
            if not record:
                return ""
            parent_path = get_full_path(record.parent_id) if record.parent_id else ""
            return f"{parent_path} - {record.name}" if parent_path else record.name

        for rec in self:
            try:
                parts = []

                if rec.country_id:
                    parts.append(rec.country_id.name)
                if rec.state_id:
                    parts.append(rec.state_id.name)
                if rec.county_id:
                    parts.append(rec.county_id.name)

                if rec.address_type == "city":
                    if rec.city_id:
                        parts.append(rec.city_id.name)
                    if rec.city_div_id:
                        parts.append(get_full_path(rec.city_div_id))
                else:
                    if rec.rural_dist_id:
                        parts.append(rec.rural_dist_id.name)
                    if rec.rural_dist_div_id:
                        parts.append(get_full_path(rec.rural_dist_div_id))

                if rec.bldg_complex_name:
                    parts.append(rec.bldg_complex_name)
                if rec.bldg_id:
                    parts.append(_("%s") % rec.bldg_id.name)
                if rec.floor_id:
                    parts.append(_("%s") % rec.floor_id.name)
                if rec.unit_id:
                    parts.append(_("%s") % rec.unit_id.name)
                if rec.postal_code:
                    parts.append(_("Postal Code:%s") % rec.postal_code)

                rec.address_text = " - ".join(filter(None, parts))

            except Exception as e:
                _logger.error("Failed to compute address for ID %s: %s", rec.id, str(e))
                rec.address_text = _("Error generating address")

    # ============================================
    # Constraints (Data Validation)
    # ============================================
    @api.constrains("postal_code_suffix")
    def _check_suffix_format(self):
        """Validate postal code suffix format based on country rules"""
        for rec in self:
            if not rec.country_id:
                continue

            rules = self.env["res.country.postal.code.rules"].search(
                [
                    ("country_id", "=", rec.country_id.id),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )

            if not rules:
                if not re.match(r"^\d{5}$", rec.postal_code_suffix):
                    raise ValidationError(
                        _("Postal Code Suffix must be exactly 5 digits!")
                    )
                continue

            suffix_pattern = "^"
            if rules.suffix_allow_letters:
                suffix_pattern += "[A-Za-z0-9]"
            else:
                suffix_pattern += "[0-9]"
            suffix_pattern += f"{{{rules.suffix_digits}}}$"

            if not re.match(suffix_pattern, rec.postal_code_suffix):
                raise ValidationError(
                    _(
                        "Postal Code Suffix must be exactly %d %s!",
                        rules.suffix_digits,
                        (
                            "alphanumeric characters"
                            if rules.suffix_allow_letters
                            else "digits"
                        ),
                    )
                )

    @api.constrains("address_type", "city_id", "rural_dist_id")
    def _check_address_structure(self):
        for rec in self:
            if rec.address_type == "city" and not rec.city_id:
                raise ValidationError("City is required for city addresses!")
            if rec.address_type == "rural_dist" and not rec.rural_dist_id:
                raise ValidationError("Rural District is required for rural addresses!")

    # ============================================
    # Record Creation Override
    # ============================================
    @api.model_create_multi
    def create(self, vals_list):
        """Create addresses without auto-generating hierarchical_id."""
        for vals in vals_list:
            address_type = vals.get("address_type", "city")

            if address_type == "city":
                if not vals.get("city_id"):
                    raise ValidationError(_("City is required for City Address type"))
                if not vals.get("city_div_id"):
                    raise ValidationError(
                        _("City Division is required for City Address type")
                    )
                if vals.get("rural_dist_id") or vals.get("rural_dist_div_id"):
                    raise ValidationError(
                        _("Rural District fields must be empty for City Address type")
                    )

            elif address_type == "rural_dist":
                if not vals.get("rural_dist_id"):
                    raise ValidationError(
                        _("Rural District is required for Rural District Address type")
                    )
                if not vals.get("rural_dist_div_id"):
                    raise ValidationError(
                        _(
                            "Rural District Division is required for Rural District Address type"
                        )
                    )
                if vals.get("city_id") or vals.get("city_div_id"):
                    raise ValidationError(
                        _("City fields must be empty for Rural District Address type")
                    )

        # Pass-through: hierarchical_id will be computed from unit_id
        return super().create(vals_list)

    def write(self, vals):
        """Ensure structural consistency on update."""
        if any(
            field in vals
            for field in [
                "address_type",
                "city_id",
                "city_div_id",
                "rural_dist_id",
                "rural_dist_div_id",
            ]
        ):
            for rec in self:
                address_type = vals.get("address_type", rec.address_type)

                if address_type == "city":
                    if "city_id" in vals and not vals["city_id"]:
                        raise ValidationError(
                            _("City is required for City Address type")
                        )
                    if "city_div_id" in vals and not vals["city_div_id"]:
                        raise ValidationError(
                            _("City Division is required for City Address type")
                        )
                    if vals.get("rural_dist_id") or vals.get("rural_dist_div_id"):
                        raise ValidationError(
                            _(
                                "Rural District fields must be empty for City Address type"
                            )
                        )
                    if not (
                        "rural_dist_id" in vals or "rural_dist_div_id" in vals
                    ) and (rec.rural_dist_id or rec.rural_dist_div_id):
                        raise ValidationError(
                            _(
                                "Rural District fields must be empty for City Address type"
                            )
                        )

                elif address_type == "rural_dist":
                    if "rural_dist_id" in vals and not vals["rural_dist_id"]:
                        raise ValidationError(
                            _(
                                "Rural District is required for Rural District Address type"
                            )
                        )
                    if "rural_dist_div_id" in vals and not vals["rural_dist_div_id"]:
                        raise ValidationError(
                            _(
                                "Rural District Division is required for Rural District Address type"
                            )
                        )
                    if vals.get("city_id") or vals.get("city_div_id"):
                        raise ValidationError(
                            _(
                                "City fields must be empty for Rural District Address type"
                            )
                        )
                    if not ("city_id" in vals or "city_div_id" in vals) and (
                        rec.city_id or rec.city_div_id
                    ):
                        raise ValidationError(
                            _(
                                "City fields must be empty for Rural District Address type"
                            )
                        )

        address_fields = [
            "country_id",
            "state_id",
            "county_id",
            "city_id",
            "city_div_id",
            "rural_dist_id",
            "rural_dist_div_id",
            "bldg_id",
            "floor_id",
            "unit_id",
            "postal_code_suffix",
            "postal_code_prefix_id",
        ]
        # if any(field in vals for field in address_fields) and not all(
        #     k in vals for k in ["latitude", "longitude"]
        # ):
        #     vals.update(
        #         {
        #             "latitude": 0.0,
        #             "longitude": 0.0,
        #         }
        #     )

        return super().write(vals)

    # ============================================
    # Onchange Handlers (User Input UI Feedback)
    # ============================================
    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id:
            return {"domain": {"state_id": [("country_id", "=", self.country_id.id)]}}
        return {}

    @api.onchange("state_id")
    def _onchange_state_id(self):
        if self.state_id:
            return {"domain": {"county_id": [("state_id", "=", self.state_id.id)]}}
        return {}

    @api.onchange("county_id")
    def _onchange_county_id(self):
        if self.county_id:
            return {
                "domain": {
                    "city_id": [("county_id", "=", self.county_id.id)],
                    "rural_dist_id": [("county_id", "=", self.county_id.id)],
                }
            }
        return {}

    @api.onchange("postal_code_suffix", "country_id")
    def _onchange_postal_code_suffix(self):
        if self.postal_code_suffix and self.country_id:
            try:
                self._check_suffix_format()
            except ValidationError as e:
                return {
                    "warning": {
                        "title": _("Invalid Postal Code Suffix"),
                        "message": e.name,
                    }
                }

    @api.onchange("city_id")
    def _onchange_city_id(self):
        if self.city_id:
            return {"domain": {"city_div_id": [("city_id", "=", self.city_id.id)]}}
        return {}

    @api.onchange("rural_dist_id")
    def _onchange_rural_dist_id(self):
        if self.rural_dist_id:
            return {
                "domain": {
                    "rural_dist_div_id": [("rural_dist_id", "=", self.rural_dist_id.id)]
                }
            }
        return {}

    @api.onchange("address_type")
    def _onchange_address_type(self):
        if self.address_type == "city":
            self.update({"rural_dist_id": False, "rural_dist_div_id": False})
        else:
            self.update({"city_id": False, "city_div_id": False})

    # ============================================
    # Utility Helpers
    # ============================================
    @api.constrains("address_type", "city_div_id", "rural_dist_div_id", "bldg_id")
    def _check_bldg_consistency(self):
        for rec in self:
            if not rec.bldg_id:
                continue
            if rec.address_type == "city":
                if rec.bldg_id.city_div_id != rec.city_div_id:
                    raise ValidationError(
                        _("Selected building must belong to the chosen city division!")
                    )
                if rec.bldg_id.rural_dist_div_id:
                    raise ValidationError(
                        _(
                            "Selected building belongs to a rural division but address is city type!"
                        )
                    )
            elif rec.address_type == "rural_dist":
                if rec.bldg_id.rural_dist_div_id != rec.rural_dist_div_id:
                    raise ValidationError(
                        _("Selected building must belong to the chosen rural division!")
                    )
                if rec.bldg_id.city_div_id:
                    raise ValidationError(
                        _(
                            "Selected building belongs to a city division but address is rural type!"
                        )
                    )

    @api.depends("city_div_id", "rural_dist_div_id")
    def _compute_available_bldg_ids(self):
        for rec in self:
            if rec.city_div_id:
                rec.available_bldg_ids = rec.city_div_id.bldg_ids
            elif rec.rural_dist_div_id:
                rec.available_bldg_ids = rec.rural_dist_div_id.bldg_ids
            else:
                rec.available_bldg_ids = False

    @api.depends("bldg_id")
    def _compute_bldg_complex_name(self):
        for rec in self:
            rec.bldg_complex_name = (
                rec.bldg_id.bldg_complex_id.name
                if rec.bldg_id.bldg_complex_id
                else False
            )

    @api.depends("floor_id")
    def _compute_available_unit_ids(self):
        for rec in self:
            if rec.floor_id:
                units = self.env["bldg.unit"].search(
                    [("floor_id", "=", rec.floor_id.id)]
                )
                rec.available_unit_ids = units
            else:
                rec.available_unit_ids = False

    @api.depends("bldg_id")
    def _compute_available_floor_ids(self):
        for rec in self:
            if rec.bldg_id:
                floors = self.env["bldg.floor"].search(
                    [("building_id", "=", rec.bldg_id.id)]
                )
                rec.available_floor_ids = floors
            else:
                rec.available_floor_ids = False

    @api.model
    def create(self, vals):
        if vals.get("bldg_id") and not vals.get("bldg_number"):
            building = self.env["bldg.building"].browse(vals["bldg_id"])
            vals["bldg_number"] = building.name
        return super().create(vals)

    @api.onchange("city_div_id", "rural_dist_div_id")
    def _onchange_clear_bldg_id(self):
        self.bldg_id = False
