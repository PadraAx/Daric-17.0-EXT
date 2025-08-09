# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BldgUnit(models.Model):
    _name = "bldg.unit"
    _description = "Building Unit or Subcomponent"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id"
    _rec_name = "display_name"

    name = fields.Char(string=_("Name"), required=True, tracking=True)
    parent_id = fields.Many2one(
        "bldg.unit", string=_("Parent Unit"), recursive=True, index=True
    )
    child_ids = fields.One2many("bldg.unit", "parent_id", string=_("Components"))

    floor_id = fields.Many2one("bldg.floor", string=_("Located On Floor"), index=True)

    unit_type_id = fields.Many2one(
        "bldg.unit.type",
        string=_("Unit Type"),
        required=True,
        tracking=True,
        index=True,
    )

    layer = fields.Selection(
        selection=[
            ("1", _("Functional Unit")),
            ("2", _("Space")),
            ("3", _("Specialized Area")),
        ],
        string=_("Hierarchy Layer"),
        compute="_compute_layer",
        recursive=True,
        store=True,
    )
    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        readonly=True,
        index=True,
        copy=False,
    )
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        recursive=True,
        index=True,
    )
    child_count = fields.Integer(
        string="Sub-units",
        compute="_compute_child_count",
        store=True,
        recursive=True,  # recompute when parent layer changes
    )
    # In bldg.unit
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
                    ("unit_id", "=", rec.id),
                    ("locked", "=", True),
                ]
            )

    # -------------------------------------------------------------------------
    #  Compute / Constraints
    # -------------------------------------------------------------------------
    @api.depends("name", "layer", "floor_id.display_name", "parent_id.display_name")
    def _compute_display_name(self):
        for rec in self:
            parts = []

            # Add floor at the beginning
            if rec.floor_id:
                parts.append(rec.floor_id.display_name or "")

            # Build the full hierarchy of units, from top-most parent to current
            unit_chain = []
            current = rec
            while current:
                unit_chain.append(current.name or "")
                current = current.parent_id

            # Reverse to have top-level parent first, then append to parts
            parts.extend(reversed(unit_chain))

            rec.display_name = " > ".join(filter(None, parts)) or "/"

    @api.depends("parent_id.layer")
    def _compute_layer(self):
        for rec in self:
            if not rec.parent_id:
                rec.layer = "1"
            elif rec.parent_id.layer == "1":
                rec.layer = "2"
            elif rec.parent_id.layer == "2":
                rec.layer = "3"
            else:
                rec.layer = False

    @api.constrains("layer", "unit_type_id")
    def _check_type_by_layer(self):
        for rec in self:
            if not rec.unit_type_id:
                continue

            allowed = rec.unit_type_id.type_allowed_layer
            if allowed == "all":
                continue

            if rec.layer != allowed:
                raise ValidationError(
                    _("The selected unit type '%s' is only allowed in Layer %s.")
                    % (rec.unit_type_id.name, allowed)
                )

            # Extra safeguard: prevent deeper nesting
            if not rec.layer:
                raise ValidationError(_("Maximum hierarchy depth (3 levels) exceeded."))

    @api.constrains("parent_id")
    def _check_no_recursive_parent(self):
        for unit in self:
            parent = unit.parent_id
            while parent:
                if parent == unit:
                    raise ValidationError(_("A unit cannot be its own ancestor."))
                parent = parent.parent_id

    @api.depends("child_ids.layer", "layer")
    def _compute_child_count(self):
        for unit in self:
            target_layer = False
            if unit.layer == "1":
                target_layer = "2"
            elif unit.layer == "2":
                target_layer = "3"

            unit.child_count = (
                len(unit.child_ids.filtered(lambda c: c.layer == target_layer))
                if target_layer
                else 0
            )

    # -------------------------------------------------------------------------
    #  On-change helpers
    # -------------------------------------------------------------------------
    @api.onchange("parent_id")
    def _onchange_filter_unit_type_by_layer(self):
        domain = []
        if not self.parent_id:
            domain = [("type_allowed_layer", "in", ["1", "all"])]
        elif self.parent_id.layer == "1":
            domain = [("type_allowed_layer", "in", ["2", "all"])]
        elif self.parent_id.layer == "2":
            domain = [("type_allowed_layer", "in", ["3", "all"])]
        return {"domain": {"unit_type_id": domain}}

    # -------------------------------------------------------------------------
    #  Display
    # -------------------------------------------------------------------------
    def name_get(self):
        return [(rec.id, f"{rec.name} ({rec.unit_type_id.code})") for rec in self]

    # -------------------------------------------------------------------------
    #  Generators
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._generate_unit_ids()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ("parent_id", "floor_id", "unit_type_id")):
            # re-generate IDs for the edited record(s) and all descendants
            self._generate_unit_ids()
            self._generate_descendant_ids()
        return res

    def _generate_descendant_ids(self):
        """Recursively regenerate IDs for all descendants."""
        for unit in self:
            unit.child_ids._generate_unit_ids()
            unit.child_ids._generate_descendant_ids()

    def _generate_unit_ids(self):
        """
        Generate hierarchical ID for each unit based on its layer:
        - Layer 1: inject at pos 30–35
        - Layer 2: inject at pos 36–41
        - Layer 3: inject at pos 42–47
        Each unit ID is always 48 characters long.
        """
        for unit in self:
            if unit.layer == "1":
                if not unit.floor_id or not unit.floor_id.hierarchical_id:
                    continue
                base_id = unit.floor_id.hierarchical_id
                scope = ("floor_id", unit.floor_id.id)
                inject_pos = (30, 36)
            elif unit.layer == "2":
                if not unit.parent_id or not unit.parent_id.hierarchical_id:
                    continue
                base_id = unit.parent_id.hierarchical_id
                scope = ("parent_id", unit.parent_id.id)
                inject_pos = (36, 42)
            elif unit.layer == "3":
                if not unit.parent_id or not unit.parent_id.hierarchical_id:
                    continue
                base_id = unit.parent_id.hierarchical_id
                scope = ("parent_id", unit.parent_id.id)
                inject_pos = (42, 48)
            else:
                continue

            if len(base_id) != 48:
                raise ValidationError(
                    _("Base hierarchical ID must be exactly 48 characters.")
                )

            type_code = (unit.unit_type_id.code or "").upper()[:4].ljust(4, "0")

            column, value = scope
            all_ids = (
                self.env["bldg.unit"]
                .search(
                    [
                        (column, "=", value),
                        ("layer", "=", unit.layer),
                        ("unit_type_id", "=", unit.unit_type_id.id),
                    ],
                    order="id",
                )
                .ids
            )
            try:
                seq = all_ids.index(unit.id) + 1
            except ValueError:
                continue

            if seq > 99:
                raise ValidationError(
                    _("Maximum 99 units of the same type per parent.")
                )

            appendix = f"{type_code}{seq:02d}"
            start, end = inject_pos

            unit.hierarchical_id = base_id[:start] + appendix + base_id[end:]
