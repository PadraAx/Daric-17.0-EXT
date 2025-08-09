from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from datetime import date
from collections import defaultdict


class BldgBuilding(models.Model):
    _name = "bldg.building"
    _description = "Building"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "hierarchical_id, name"
    _rec_name = "display_name"
    _sql_constraints = [
        (
            "hierarchical_id_unique",
            "unique(hierarchical_id)",
            "Hierarchical ID must be unique.",
        )
    ]
    _indexes = [
        ("bldg_building_physical_type_id_idx", ["physical_type_id"]),
        ("bldg_building_state_idx", ["state"]),
        ("bldg_building_category_id_idx", ["category_id"]),
        ("bldg_building_hierarchical_id_idx", ["hierarchical_id"]),
    ]

    # ============================================================================
    # BASIC INFO
    # ============================================================================
    name = fields.Char(string=_("Name"), required=True, tracking=True, index=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    active = fields.Boolean(string=_("Active"), default=True, tracking=True)
    sequence = fields.Integer(string=_("Sequence"), default=10)

    # ============================================================================
    # CONTEXT & STRUCTURE
    # ============================================================================
    context_type = fields.Selection(
        selection=[
            ("complex", _("In a Complex")),
            ("standalone", _("Standalone")),
        ],
        string=_("Context"),
        default="standalone",
        required=True,
        tracking=True,
    )
    bldg_complex_id = fields.Many2one(
        comodel_name="bldg.group",
        string=_("Building Complex"),
        domain="""[
            ('is_complex', '=', True),
            '|',
                '&', ('city_div_id', '=', city_div_id), ('location_type', '=', 'urban'),
                '&', ('rural_dist_div_id', '=', rural_dist_div_id), ('location_type', '=', 'rural')
        ]""",
    )
    physical_type_id = fields.Many2one(
        "bldg.building.physical.type",
        string="Physical Type",
        ondelete="restrict",
        index=True,
    )
    # ============================================================================
    # CLASSIFICATION
    # ============================================================================
    category_id = fields.Many2one(
        comodel_name="bldg.category",
        string=_("Category"),
        required=True,
        tracking=True,
    )
    category_description = fields.Text(
        string=_("Category Description"),
        related="category_id.description",
        readonly=True,
    )
    # ============================================================================
    # STATUS & IDENTIFIERS
    # ============================================================================
    image = fields.Image(string=_("Image"))
    notes = fields.Html(string=_("Notes"))
    # ============================================================================
    # REGIONAL DATA
    # ============================================================================
    location_type = fields.Selection(
        selection=[
            ("urban", _("Urban")),
            ("rural", _("Rural")),
        ],
        string=_("Location Type"),
        required=True,
        tracking=True,
        index=True,
    )
    city_id = fields.Many2one(
        "res.city",
        string=_("City"),
        tracking=True,
    )

    city_div_id = fields.Many2one(
        "res.city.div",
        string=_("City Division"),
        domain="[('city_id', '=', city_id)]",
        tracking=True,
    )

    rural_dist_id = fields.Many2one(
        "res.rural.dist",
        string=_("Rural District"),
        domain="[('id','in',available_district_ids)]",
        tracking=True,
    )
    rural_dist_div_id = fields.Many2one(
        "res.rural.dist.div",
        string=_("Rural Division"),
        domain="[('rural_dist_id','=',rural_dist_id)]",
        tracking=True,
    )
    available_city_ids = fields.Many2many(
        "res.city",
        compute="_compute_available_locations",
        store=True,
    )
    available_district_ids = fields.Many2many(
        "res.rural.dist",
        compute="_compute_available_locations",
        store=True,
    )
    hierarchical_id = fields.Char(
        string="Hierarchical ID", readonly=True, index=True, copy=False
    )
    floor_ids = fields.One2many("bldg.floor", "building_id", string=_("Floors"))
    floor_count = fields.Integer(
        string=_("Floor Count"),
        compute="_compute_floor_count",
        store=True,
    )
    # In bldg.building  (48-char hierarchical_id holder for buildings)
    locked_profile_ids = fields.One2many(
        comodel_name="bldg.prof",
        compute="_compute_locked_profiles",
        string="Locked Profiles",
    )

    @api.depends("hierarchical_id")
    def _compute_locked_profiles(self):
        for rec in self:
            rec.locked_profile_ids = self.env["bldg.prof"].search(
                [
                    ("profile_level", "=", "building"),
                    ("building_id", "=", rec.id),
                    ("locked", "=", True),
                ]
            )

    # ============================================================================
    # COMPUTE METHODS
    # ============================================================================
    @api.depends(
        "name",
        "location_type",
        "city_id",
        "city_div_id",
        "rural_dist_id",
        "rural_dist_div_id",
        "context_type",
        "bldg_complex_id",
    )
    def _compute_display_name(self):
        for record in self:
            parts = []

            # 1) City / District hierarchy
            if record.location_type == "urban":
                if record.city_id:
                    parts.append(record.city_id.name)
                if record.city_div_id:
                    parts.append(record.city_div_id.name)
            elif record.location_type == "rural":
                if record.rural_dist_id:
                    parts.append(record.rural_dist_id.name)
                if record.rural_dist_div_id:
                    parts.append(record.rural_dist_div_id.name)

            # 2) Complex name when inside a complex
            if record.context_type == "complex" and record.bldg_complex_id:
                parts.append(record.bldg_complex_id.name)

            # 3) Building’s own name
            parts.append(record.name or "")

            record.display_name = " > ".join(filter(None, parts))

    @api.depends("location_type")
    def _compute_available_locations(self):
        for record in self:
            if record.location_type == "urban":
                record.available_city_ids = self.env["res.city"].search([])
                record.available_district_ids = False
            else:
                record.available_district_ids = self.env["res.rural.dist"].search([])
                record.available_city_ids = False

    @api.depends("floor_ids")
    def _compute_floor_count(self):
        for bldg in self:
            bldg.floor_count = len(bldg.floor_ids)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.display_name
            if not name:
                # Safe fallback (in case compute didn't run yet)
                parts = []
                if rec.location_type == "urban":
                    if rec.city_id:
                        parts.append(rec.city_id.name)
                    if rec.city_div_id:
                        parts.append(rec.city_div_id.name)
                elif rec.location_type == "rural":
                    if rec.rural_dist_id:
                        parts.append(rec.rural_dist_id.name)
                    if rec.rural_dist_div_id:
                        parts.append(rec.rural_dist_div_id.name)
                parts.append(rec.name or "")
                name = " > ".join(filter(None, parts))
            result.append((rec.id, name))
        return result

    # ============================================================================
    # CONSTRAINT METHODS
    # ============================================================================
    @api.constrains("context_type", "bldg_complex_id")
    def _check_complex_required(self):
        for rec in self:
            if rec.context_type == "complex" and not rec.bldg_complex_id:
                raise ValidationError(
                    _("Building Complex must be set when context is 'In a Complex'.")
                )

    @api.constrains("city_div_id", "rural_dist_div_id", "location_type")
    def _check_location_exclusivity(self):
        for record in self:
            if record.location_type == "urban" and not record.city_div_id:
                raise ValidationError(
                    _("Urban buildings must be linked to a city division")
                )
            if record.location_type == "rural" and not record.rural_dist_div_id:
                raise ValidationError(
                    _("Rural buildings must be linked to a rural district division")
                )
            if record.city_div_id and record.rural_dist_div_id:
                raise ValidationError(
                    _("Cannot belong to both city and rural divisions")
                )

    # ============================================================================
    # ONCHANGE METHODS
    # ============================================================================
    @api.onchange("context_type")
    def _onchange_context_type(self):
        if self.context_type == "standalone":
            self.bldg_complex_id = False

    # ============================================================================
    # CRUD METHODS
    # ============================================================================
    @api.model_create_multi
    def create(self, vals_list):
        # === original bulk-fetches (unchanged) ===
        division_ids = {"city": set(), "rural": set()}
        complex_ids = set()
        for vals in vals_list:
            if vals.get("city_div_id"):
                division_ids["city"].add(vals["city_div_id"])
            elif vals.get("rural_dist_div_id"):
                division_ids["rural"].add(vals["rural_dist_div_id"])
            if vals.get("bldg_complex_id"):
                complex_ids.add(vals["bldg_complex_id"])

        division_codes = {}
        if division_ids["city"]:
            divisions = self.env["res.city.div"].browse(division_ids["city"])
            division_codes.update({d.id: d.hierarchical_id for d in divisions})
        if division_ids["rural"]:
            divisions = self.env["res.rural.dist.div"].browse(division_ids["rural"])
            division_codes.update({d.id: d.hierarchical_id for d in divisions})

        complex_sequences = {}
        if complex_ids:
            complexes = self.env["bldg.group"].browse(complex_ids)
            complex_sequences.update({c.id: c.sequence for c in complexes})

        # === create records ===
        records = super().create(vals_list)

        # === generate hierarchical IDs ===
        self._assign_building_ids(records)
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(
            f in vals
            for f in (
                "bldg_complex_id",
                "context_type",
                "city_div_id",
                "rural_dist_div_id",
            )
        ):
            self._assign_building_ids(self)
        return res

    # ============================================================================
    # BUSINESS METHODS
    # ============================================================================
    def get_full_location(self):
        """Returns complete location information as a string"""
        self.ensure_one()
        if self.location_type == "urban" and self.city_div_id:
            return f"{self.city_div_id.name}, {self.city_id.name}"
        elif self.location_type == "rural" and self.rural_dist_div_id:
            return f"{self.rural_dist_div_id.name}, {self.rural_dist_id.name}"
        return _("Location not specified")

    def name_get(self):
        return [(rec.id, rec.display_name or rec.name) for rec in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []

        if name:
            domain = [
                "|",
                "|",
                ("name", operator, name),
                ("display_name", operator, name),
                ("hierarchical_id", operator, name),
            ]

        return self.search(domain + args, limit=limit).name_get()

    # ---------------------------------------------------------
    # helper
    # ---------------------------------------------------------
    def _assign_building_ids(self, records):
        for bldg in records:
            if bldg.hierarchical_id:
                continue

            div = bldg.city_div_id or bldg.rural_dist_div_id
            if not div or not div.hierarchical_id or len(div.hierarchical_id) != 12:
                raise ValidationError(
                    _("Building must be linked to a valid 12-digit division")
                )

            if bldg.context_type == "complex":
                cx = bldg.bldg_complex_id
                if not cx or not cx.hierarchical_id or len(cx.hierarchical_id) != 48:
                    raise ValidationError(
                        _("Complex must already have a valid 48-character ID")
                    )
                prefix = cx.hierarchical_id
                key_scope = ("bldg_complex_id", cx.id)
            else:
                if len(div.hierarchical_id) != 12:
                    raise ValidationError(_("Division ID must be 12 characters"))
                prefix = (div.hierarchical_id + "000000").ljust(48, "0")
                if bldg.location_type == "urban":
                    key_scope = ("city_div_id", div.id)
                else:
                    key_scope = ("rural_dist_div_id", div.id)

            cat_code = (bldg.category_id.code or "")[:4].ljust(4, "0")
            type_code = (bldg.physical_type_id.code or "")[:2].ljust(2, "0")

            key_stub = prefix[:18] + cat_code + type_code

            column, value = key_scope
            self.env.cr.execute(
                f"""
                SELECT COUNT(*)
                FROM bldg_building
                WHERE {column} = %s
                AND SUBSTRING(hierarchical_id FROM 1 FOR 26) = %s
                """,
                (value, key_stub),
            )
            seq = self.env.cr.fetchone()[0] + 1
            if seq > 99:
                raise ValidationError(_("Maximum 99 buildings per combination"))

            final_id = prefix[:18] + cat_code + type_code + f"{seq:02d}" + prefix[26:]
            bldg.hierarchical_id = final_id
