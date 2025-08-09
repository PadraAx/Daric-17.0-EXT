# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from collections import defaultdict


class BldgGroup(models.Model):
    _name = "bldg.group"
    _description = "Building Group"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec = "display_name"
    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------
    name = fields.Char(string="Group Name", required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    description = fields.Html(
        string="Description",
        sanitize=True,
        sanitize_attributes=True,
        sanitize_form=True,
        strip_style=True,
        tracking=True,
        prefetch=False,
        help="Detailed description of the Complex",
    )

    location_type = fields.Selection(
        [("urban", _("Urban")), ("rural", _("Rural"))],
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
        domain="[('id', 'in', available_district_ids)]",
        tracking=True,
    )
    rural_dist_div_id = fields.Many2one(
        "res.rural.dist.div",
        string=_("Rural Division"),
        domain="[('rural_dist_id', '=', rural_dist_id)]",
        tracking=True,
    )

    available_city_ids = fields.Many2many(
        "res.city",
        compute="_compute_available_locations",
        store=False,
    )
    available_district_ids = fields.Many2many(
        "res.rural.dist",
        compute="_compute_available_locations",
        store=False,
    )

    bldg_ids = fields.One2many(
        "bldg.building",
        "bldg_complex_id",
        string="Buildings in Group",
    )
    bldg_count = fields.Integer(
        string="Building Count",
        compute="_compute_bldg_count",
        store=True,
        readonly=True,
    )
    is_complex = fields.Boolean(string="Is a Building Complex", default=True)

    bldg_group_type_id = fields.Many2one(
        comodel_name="bldg.group.type",
        string=_("Building Complex Type"),
        required=True,
        tracking=True,
    )

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        readonly=True,
        index=True,
        copy=False,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    # In bldg.group   (48-char hierarchical_id holder for building-complexes)
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
                    ("profile_level", "=", "building_complex"),
                    ("group_id", "=", rec.id),
                    ("locked", "=", True),
                ]
            )

    # ------------------------------------------------------------------
    # Computed
    # ------------------------------------------------------------------
    @api.depends("location_type")
    def _compute_available_locations(self):
        for rec in self:
            if rec.location_type == "urban":
                rec.available_city_ids = self.env["res.city"].search([])
                rec.available_district_ids = False
            else:
                rec.available_district_ids = self.env["res.rural.dist"].search([])
                rec.available_city_ids = False

    @api.depends("bldg_ids")
    def _compute_bldg_count(self):
        for rec in self:
            rec.bldg_count = len(rec.bldg_ids)

    @api.depends(
        "name",
        "location_type",
        "city_id",
        "city_div_id",
        "rural_dist_id",
        "rural_dist_div_id",
    )
    def _compute_display_name(self):
        for record in self:
            parts = []

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

            parts.append(record.name or "")
            record.display_name = " > ".join(filter(None, parts))

    # ------------------------------------------------------------------
    # Onchange helpers
    # ------------------------------------------------------------------
    @api.onchange("location_type")
    def _onchange_location_type(self):
        """Reset all location fields when the type flips."""
        self.update(
            {
                "city_id": False,
                "city_div_id": False,
                "rural_dist_id": False,
                "rural_dist_div_id": False,
            }
        )

    @api.onchange("city_id")
    def _onchange_city_id(self):
        self.city_div_id = False

    @api.onchange("rural_dist_id")
    def _onchange_rural_dist_id(self):
        self.rural_dist_div_id = False

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("city_div_id", "rural_dist_div_id", "location_type")
    def _check_location_integrity(self):
        for rec in self:
            if rec.location_type == "urban":
                if not rec.city_div_id:
                    raise ValidationError(
                        _("Urban complexes must belong to a city division.")
                    )
                if rec.rural_dist_div_id:
                    raise ValidationError(
                        _("Urban complexes cannot be linked to a rural division.")
                    )
            else:
                if not rec.rural_dist_div_id:
                    raise ValidationError(
                        _("Rural complexes must belong to a rural district division.")
                    )
                if rec.city_div_id:
                    raise ValidationError(
                        _("Rural complexes cannot be linked to a city division.")
                    )

    @api.constrains("city_div_id", "rural_dist_div_id")
    def _lock_parent_when_buildings(self):
        for rec in self:
            if rec.bldg_ids:
                if rec.location_type == "urban":
                    if rec.city_div_id != rec.bldg_ids[0].city_div_id:
                        raise ValidationError(
                            _("Cannot change city division while buildings are linked.")
                        )
                else:
                    if rec.rural_dist_div_id != rec.bldg_ids[0].rural_dist_div_id:
                        raise ValidationError(
                            _(
                                "Cannot change rural division while buildings are linked."
                            )
                        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered("is_complex")._assign_complex_ids()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"city_div_id", "rural_dist_div_id"} & vals.keys():
            self._assign_complex_ids()
        return res

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _assign_complex_ids(self):
        """
        Generate 18-character hierarchical IDs for complexes:
        [12-character parent] + [4-character type code] + [2-digit seq]
        Sequence starts at 01 for the first complex of each type in a division.
        """
        parent_map = defaultdict(lambda: self.env["bldg.group"])
        for cx in self:
            parent = cx.city_div_id or cx.rural_dist_div_id
            if not parent or len(parent.hierarchical_id or "") != 12:
                raise ValidationError(
                    _("Parent division must have a 12-character hierarchical ID.")
                )
            if (
                not cx.bldg_group_type_id
                or not cx.bldg_group_type_id.code
                or len(cx.bldg_group_type_id.code) != 4
            ):
                raise ValidationError(
                    _("Building group type must have a 4-character code.")
                )
            parent_map[parent] |= cx

        for parent, complexes in parent_map.items():
            # Advisory lock to prevent race conditions
            self.env.cr.execute("SELECT pg_advisory_xact_lock(%s)", (parent.id,))

            # Group complexes by type to count sequences per type
            type_groups = defaultdict(lambda: self.env["bldg.group"])
            for cx in complexes:
                type_groups[cx.bldg_group_type_id] |= cx

            # Process each type separately
            for group_type, type_complexes in type_groups.items():
                # Count existing complexes of this type under the same parent
                self.env.cr.execute(
                    """
                    SELECT COUNT(*) FROM bldg_group
                    WHERE (city_div_id = %s OR rural_dist_div_id = %s)
                    AND bldg_group_type_id = %s
                    AND is_complex = True
                    AND id NOT IN %s
                    """,
                    (parent.id, parent.id, group_type.id, tuple(type_complexes.ids)),
                )
                existing_count = self.env.cr.fetchone()[0] or 0

                # Assign IDs with type code + sequence (no trailing zeros)
                for seq, cx in enumerate(type_complexes, start=existing_count + 1):
                    if seq > 99:
                        raise ValidationError(
                            _("Maximum 99 complexes allowed per type in a division.")
                        )
                    # Format: 12 (parent) + 4 (type code) + 2 (seq)
                    cx.hierarchical_id = (
                        f"{parent.hierarchical_id}{group_type.code}{seq:02d}".ljust(
                            48, "0"
                        )
                    )
