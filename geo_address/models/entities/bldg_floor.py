# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BldgFloor(models.Model):
    _name = "bldg.floor"
    _description = "Building Floor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "level_number, id"
    _sql_constraints = [
        (
            "hierarchical_id_unique",
            "unique(hierarchical_id)",
            "Hierarchical ID must be unique.",
        )
    ]

    name = fields.Char(string=_("Name"), required=True, tracking=True)
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )

    hierarchical_id = fields.Char(
        string="Hierarchical ID", readonly=True, index=True, copy=False, tracking=True
    )
    level_number = fields.Integer(
        string=_("Floor Number"),
        tracking=True,
        required=True,
        help=_("Used for sorting and identification (-99 to 99)"),
    )

    building_id = fields.Many2one(
        "bldg.building",
        string=_("Building"),
        required=True,
        index=True,
        ondelete="cascade",
    )
    unit_ids = fields.One2many("bldg.unit", "floor_id", string=_("Units"))
    unit_count = fields.Integer(
        string=_("Unit Count"),
        compute="_compute_unit_count",
        store=True,
        readonly=True,
    )

    floor_type_id = fields.Many2one(
        comodel_name="bldg.floor.type",
        string=_("Floor Type"),
        required=True,
        tracking=True,
    )
    # In bldg.floor
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
                    ("profile_level", "=", "floor"),
                    ("floor_id", "=", rec.id),
                    ("locked", "=", True),
                ]
            )

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains("level_number")
    def _check_level_number(self):
        for rec in self:
            if not -99 <= rec.level_number <= 99:
                raise ValidationError(_("Floor number must be between -99 and 99"))

    # -------------------------------------------------------------------------
    # Computes
    # -------------------------------------------------------------------------
    @api.depends("unit_ids.layer")
    def _compute_unit_count(self):
        for rec in self:
            rec.unit_count = len(rec.unit_ids.filtered(lambda u: u.layer == "1"))

    @api.depends("name", "building_id.display_name")
    def _compute_display_name(self):
        for rec in self:
            building_name = rec.building_id.display_name or _("Unknown Building")
            rec.display_name = f"{building_name} > {rec.name or ''}"

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._generate_hierarchical_ids()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ("building_id", "level_number", "floor_type_id")):
            self._generate_hierarchical_ids()
        return res

    # -------------------------------------------------------------------------
    # Business
    # -------------------------------------------------------------------------
    def _generate_hierarchical_ids(self):
        for floor in self:
            if not floor.building_id or not floor.building_id.hierarchical_id:
                continue

            building_id = floor.building_id.hierarchical_id
            if len(building_id) != 48:
                raise ValidationError(
                    _("Building hierarchical ID must be exactly 48 characters")
                )

            type_code = (floor.floor_type_id.code or "")[:2].upper().ljust(2, "0")

            seq = (
                self.env["bldg.floor"].search_count(
                    [
                        ("building_id", "=", floor.building_id.id),
                        ("floor_type_id", "=", floor.floor_type_id.id),
                        ("id", "!=", floor.id),
                    ]
                )
                + 1
            )
            if seq > 99:
                raise ValidationError(
                    _("Maximum 99 floors of the same type per building")
                )

            appendix = f"{type_code}{seq:02d}"

            # Replace characters 27–30 (index 26 to 30)
            floor.hierarchical_id = building_id[:26] + appendix + building_id[30:]

    def name_get(self):
        return [
            (rec.id, f"{rec.building_id.name or ''} - {rec.name} (L{rec.level_number})")
            for rec in self
        ]
