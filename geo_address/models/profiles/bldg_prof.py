# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# Constants unchanged
LEVELS = [
    ("building_complex", "Building Complex"),
    ("building", "Building"),
    ("floor", "Floor"),
    ("unit", "Unit"),
    ("unit_component", "Unit Component"),
    ("unit_sub_component", "Unit Sub-Component"),
]


class BldgProfile(models.Model):
    _name = "bldg.prof"
    _description = _("Building / Component Attribute Profile")
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "display_name"
    _order = "hierarchical_id, id"

    _sql_constraints = [
        ("hier_uniq", "UNIQUE(hierarchical_id)", _("Hierarchical ID must be unique.")),
    ]

    # ---------------------------------------------------------------------
    # FIELDS – unchanged definitions (kept for completeness)
    # ---------------------------------------------------------------------
    name = fields.Char(required=True, index=True)
    display_name = fields.Char(compute="_compute_display_name", store=True, index=True)
    profiling_date = fields.Datetime(
        string="Profiling Date",
        required=True,
        default=fields.Datetime.now,
        help="Point in time when this snapshot was taken",
    )
    issuer_id = fields.Many2one(
        "res.partner", string="Issuer", ondelete="restrict", index=True
    )

    profile_level = fields.Selection(
        LEVELS, string="Profile Level", required=True, index=True
    )

    parent_id = fields.Many2one(
        "bldg.prof",
        string="Parent Profile",
        compute="_compute_parent_id",
        store=True,
        index=True,
        readonly=False,  # allow the UI to set it if necessary
    )
    child_ids = fields.One2many(
        "bldg.prof",
        "parent_id",
        string="Child Profiles",
    )

    group_id = fields.Many2one(
        "bldg.group", string="Building Group", ondelete="restrict", index=True
    )
    building_id = fields.Many2one(
        "bldg.building", string="Building", ondelete="restrict", index=True
    )
    building_context_type = fields.Selection(
        related="building_id.context_type",
        store=True,
        readonly=True,
        string="Building Context Type",
    )

    floor_id = fields.Many2one(
        "bldg.floor", string="Floor", ondelete="restrict", index=True
    )

    unit_id = fields.Many2one(
        "bldg.unit",
        string="Unit / Component",
        ondelete="restrict",
        index=True,
        domain="[('layer', '=', expected_layer)]",
    )
    unit_layer = fields.Selection(
        related="unit_id.layer", store=True, readonly=True, string="Unit Layer"
    )
    expected_layer = fields.Char(compute="_compute_expected_layer", store=False)

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        store=True,
        readonly=True,
        copy=False,
        index=True,
    )

    locked = fields.Boolean(
        string="Locked",
        default=False,
        readonly=True,
        help="When a newer profile exists this record becomes read-only.",
    )
    can_edit = fields.Boolean(compute="_compute_can_edit")

    @api.depends("locked")
    def _compute_can_edit(self):
        for rec in self:
            rec.can_edit = not rec.locked

    attribute_line_ids = fields.One2many(
        "bldg.profile.attribute.line",
        "profile_id",
        string="Attribute Lines",
        help="Profile-specific values for linked attributes.",
    )
    score = fields.Float(
        string="Total Score",
        compute="_compute_score",
        store=True,
    )

    @api.depends("attribute_line_ids.points")
    def _compute_score(self):
        for prof in self:
            prof.score = sum(prof.attribute_line_ids.mapped("points"))

    # ---------------------------------------------------------------------
    # COMPUTE / ONCHANGE / CONSTRAINS – unchanged (kept for completeness)
    # ---------------------------------------------------------------------
    @api.depends("name", "profile_level")
    def _compute_display_name(self):
        for rec in self:
            level_name = dict(LEVELS).get(rec.profile_level, "")
            rec.display_name = f"{rec.name} [{level_name}]"

    @api.depends("profile_level")
    def _compute_expected_layer(self):
        layer_map = {
            "unit": "1",
            "unit_component": "2",
            "unit_sub_component": "3",
        }
        for rec in self:
            rec.expected_layer = layer_map.get(rec.profile_level, False)

    @api.depends("hierarchical_id")
    def _compute_parent_id(self):
        for rec in self:
            if not rec.hierarchical_id or len(rec.hierarchical_id) < 60:
                rec.parent_id = False
                continue

            hierarchy_key = rec.hierarchical_id[-12:]  # the rightmost 12 characters
            levels = [hierarchy_key[i : i + 2] for i in range(0, 12, 2)]

            # Find the last non-zero level
            try:
                last_nonzero_idx = max(
                    idx for idx, val in enumerate(levels) if val != "00"
                )
            except ValueError:
                rec.parent_id = False
                continue  # No levels at all

            # If it's a root node (only one level filled)
            if last_nonzero_idx == 0:
                rec.parent_id = False
                continue

            # Build parent's 12-char suffix
            parent_levels = levels[:last_nonzero_idx] + ["00"] * (6 - last_nonzero_idx)
            parent_suffix = "".join(parent_levels)

            parent_hierarchical_id = rec.hierarchical_id[:-12] + parent_suffix

            parent = self.search(
                [("hierarchical_id", "=", parent_hierarchical_id)], limit=1
            )
            rec.parent_id = parent if parent else False

    @api.onchange("profile_level")
    def _onchange_profile_level(self):
        self.update(
            {
                "group_id": False,
                "building_id": False,
                "floor_id": False,
                "unit_id": False,
                "parent_id": False,
            }
        )

    @api.onchange("profile_level", "building_id", "floor_id")
    def _onchange_level_or_parent(self):
        level = self.profile_level
        resets = {}
        if level != "floor":
            resets["floor_id"] = False
        if level not in ("unit", "unit_component", "unit_sub_component"):
            resets["unit_id"] = False
        if resets:
            self.update(resets)

    @api.constrains("profile_level", "group_id", "building_id", "floor_id", "unit_id")
    def _check_links_by_level(self):
        for rec in self:
            level = rec.profile_level
            valid = {
                "building_complex": bool(
                    rec.group_id
                    and not any([rec.building_id, rec.floor_id, rec.unit_id])
                ),
                "building": bool(
                    rec.building_id
                    and not any([rec.group_id, rec.floor_id, rec.unit_id])
                ),
                "floor": bool(
                    rec.floor_id
                    and not any([rec.group_id, rec.building_id, rec.unit_id])
                ),
                "unit": bool(
                    rec.unit_id
                    and not any([rec.group_id, rec.building_id, rec.floor_id])
                ),
                "unit_component": bool(
                    rec.unit_id
                    and not any([rec.group_id, rec.building_id, rec.floor_id])
                ),
                "unit_sub_component": bool(
                    rec.unit_id
                    and not any([rec.group_id, rec.building_id, rec.floor_id])
                ),
            }
            if not valid.get(level):
                raise ValidationError(
                    _("Invalid link combination for level '%s'.") % level
                )

    # ---------------------------------------------------------------------
    # HIERARCHICAL_ID ALGORITHM – fully updated to NEW spec
    # ---------------------------------------------------------------------
    def _compute_hierarchical_id(self, vals):
        """
        Build the 60-char hierarchical_id exactly as defined in the
        updated algorithm document (validation + slicing rules).
        """
        level = vals.get("profile_level", self.profile_level)
        if level not in dict(LEVELS):
            return vals
        if vals.get("hierarchical_id"):
            return vals  # manual override allowed

        env = self.env
        new_id = None

        # -------------------------------------------------
        # 1. BUILDING_COMPLEX
        # -------------------------------------------------
        if level == "building_complex":
            group_id = vals.get("group_id") or self.group_id.id
            if not group_id:
                raise ValidationError(
                    _("Group is required to create a building_complex profile.")
                )
            group = env["bldg.group"].browse(group_id)
            base = group.hierarchical_id
            if not base or len(base) != 48:
                raise ValidationError(
                    _("Group must have a 48-character hierarchical ID.")
                )

            seq = (
                env["bldg.prof"].search_count(
                    [
                        ("group_id", "=", group.id),
                        ("profile_level", "=", "building_complex"),
                    ]
                )
                + 1
            )
            new_id = f"{base}{seq:02}0000000000"

        # -------------------------------------------------
        # 2. BUILDING
        # -------------------------------------------------
        elif level == "building":
            building_id = vals.get("building_id") or self.building_id.id
            if not building_id:
                raise ValidationError(
                    _("Building is required to create a building-level profile.")
                )
            building = env["bldg.building"].browse(building_id)

            if building.context_type == "complex":
                parent_id = vals.get("parent_id") or self.parent_id.id
                if not parent_id:
                    raise ValidationError(
                        _("Parent is required for building in a complex.")
                    )
                parent = env["bldg.prof"].browse(parent_id)
                parent_hier = parent.hierarchical_id
                if not parent_hier or len(parent_hier) != 60:
                    raise ValidationError(
                        _("Parent must have a 60-character hierarchical ID.")
                    )

                bldg_hier = building.hierarchical_id
                if not bldg_hier or len(bldg_hier) != 48:
                    raise ValidationError(
                        _("Building must have a 48-character hierarchical ID.")
                    )
                if bldg_hier[:18] != parent_hier[:18]:
                    raise ValidationError(
                        _(
                            "This Building doesn’t belong to the same profiled Building Complex "
                            "with the %s profile ID"
                        )
                        % parent_hier
                    )

                seq = (
                    env["bldg.prof"].search_count(
                        [
                            ("building_id", "=", building.id),
                            ("profile_level", "=", "building"),
                        ]
                    )
                    + 1
                )
                new_id = f"{bldg_hier}{parent_hier[48:50]}{seq:02}00000000"

            elif building.context_type == "standalone":
                base = building.hierarchical_id
                if not base or len(base) != 48:
                    raise ValidationError(
                        _("Building must have a 48-character hierarchical ID.")
                    )
                seq = (
                    env["bldg.prof"].search_count(
                        [
                            ("building_id", "=", building.id),
                            ("profile_level", "=", "building"),
                        ]
                    )
                    + 1
                )
                new_id = f"{base}00{seq:02}00000000"

            else:
                raise ValidationError(
                    _("Unknown building context type: %s") % building.context_type
                )

        # -------------------------------------------------
        # 3. FLOOR
        # -------------------------------------------------
        elif level == "floor":
            parent_id = vals.get("parent_id") or self.parent_id.id
            if not parent_id:
                raise ValidationError(
                    _("Parent is required to create a floor-level profile.")
                )
            parent = env["bldg.prof"].browse(parent_id)
            parent_hier = parent.hierarchical_id
            if not parent_hier or len(parent_hier) != 60:
                raise ValidationError(
                    _("Parent must have a 60-character hierarchical ID.")
                )

            floor_id = vals.get("floor_id") or self.floor_id.id
            if not floor_id:
                raise ValidationError(
                    _("Floor is required to create a floor-level profile.")
                )
            floor = env["bldg.floor"].browse(floor_id)
            floor_hier = floor.hierarchical_id
            if not floor_hier or len(floor_hier) != 48:
                raise ValidationError(
                    _("Floor must have a 48-character hierarchical ID.")
                )

            if floor_hier[:26] != parent_hier[:26]:
                raise ValidationError(
                    _(
                        "This Floor doesn’t belong to the same profiled Building "
                        "with the %s Profile ID"
                    )
                    % parent_hier
                )

            seq = (
                env["bldg.prof"].search_count(
                    [("floor_id", "=", floor.id), ("profile_level", "=", "floor")]
                )
                + 1
            )
            new_id = f"{floor_hier}{parent_hier[48:52]}{seq:02}000000"

        # -------------------------------------------------
        # 4. UNIT
        # -------------------------------------------------
        elif level == "unit":
            parent_id = vals.get("parent_id") or self.parent_id.id
            if not parent_id:
                raise ValidationError(
                    _("Parent is required to create a unit-level profile.")
                )
            parent = env["bldg.prof"].browse(parent_id)
            parent_hier = parent.hierarchical_id
            if not parent_hier or len(parent_hier) != 60:
                raise ValidationError(
                    _("Parent must have a 60-character hierarchical ID.")
                )

            unit_id = vals.get("unit_id") or self.unit_id.id
            if not unit_id:
                raise ValidationError(
                    _("Unit is required to create a unit-level profile.")
                )
            unit = env["bldg.unit"].browse(unit_id)
            if unit.layer != "1":
                raise ValidationError(
                    _("Only units with layer = 1 can be linked to a 'unit' profile.")
                )
            unit_hier = unit.hierarchical_id
            if not unit_hier or len(unit_hier) != 48:
                raise ValidationError(
                    _("Unit must have a 48-character hierarchical ID.")
                )

            if unit_hier[:30] != parent_hier[:30]:
                raise ValidationError(
                    _(
                        "This Unit doesn’t belong to the same profiled Floor "
                        "with the %s Profile ID"
                    )
                    % parent_hier
                )

            seq = (
                env["bldg.prof"].search_count(
                    [("unit_id", "=", unit.id), ("profile_level", "=", "unit")]
                )
                + 1
            )
            new_id = f"{unit_hier}{parent_hier[48:54]}{seq:02}0000"

        # -------------------------------------------------
        # 5. UNIT_COMPONENT
        # -------------------------------------------------
        elif level == "unit_component":
            parent_id = vals.get("parent_id") or self.parent_id.id
            if not parent_id:
                raise ValidationError(
                    _("Parent is required to create a unit_component-level profile.")
                )
            parent = env["bldg.prof"].browse(parent_id)
            parent_hier = parent.hierarchical_id
            if not parent_hier or len(parent_hier) != 60:
                raise ValidationError(
                    _("Parent must have a 60-character hierarchical ID.")
                )

            unit_id = vals.get("unit_id") or self.unit_id.id
            if not unit_id:
                raise ValidationError(
                    _("Unit is required to create a unit_component-level profile.")
                )
            unit = env["bldg.unit"].browse(unit_id)
            if unit.layer != "2":
                raise ValidationError(
                    _(
                        "Only units with layer = 2 can be linked to a 'unit_component' profile."
                    )
                )
            unit_hier = unit.hierarchical_id
            if not unit_hier or len(unit_hier) != 48:
                raise ValidationError(
                    _("Unit must have a 48-character hierarchical ID.")
                )

            if unit_hier[:36] != parent_hier[:36]:
                raise ValidationError(
                    _(
                        "This Unit Component doesn’t belong to the same profiled Unit "
                        "with the %s Profile ID"
                    )
                    % parent_hier
                )

            seq = (
                env["bldg.prof"].search_count(
                    [
                        ("unit_id", "=", unit.id),
                        ("profile_level", "=", "unit_component"),
                    ]
                )
                + 1
            )
            new_id = f"{unit_hier}{parent_hier[48:56]}{seq:02}00"

        # -------------------------------------------------
        # 6. UNIT_SUB_COMPONENT
        # -------------------------------------------------
        elif level == "unit_sub_component":
            parent_id = vals.get("parent_id") or self.parent_id.id
            if not parent_id:
                raise ValidationError(
                    _(
                        "Parent is required to create a unit_sub_component-level profile."
                    )
                )
            parent = env["bldg.prof"].browse(parent_id)
            parent_hier = parent.hierarchical_id
            if not parent_hier or len(parent_hier) != 60:
                raise ValidationError(
                    _("Parent must have a 60-character hierarchical ID.")
                )

            unit_id = vals.get("unit_id") or self.unit_id.id
            if not unit_id:
                raise ValidationError(
                    _("Unit is required to create a unit_sub_component-level profile.")
                )
            unit = env["bldg.unit"].browse(unit_id)
            if unit.layer != "3":
                raise ValidationError(
                    _(
                        "Only units with layer = 3 can be linked to a 'unit_sub_component' profile."
                    )
                )
            unit_hier = unit.hierarchical_id
            if not unit_hier or len(unit_hier) != 48:
                raise ValidationError(
                    _("Unit must have a 48-character hierarchical ID.")
                )

            if unit_hier[:36] != parent_hier[:36]:
                raise ValidationError(
                    _(
                        "This Unit SubComponent doesn’t belong to the same profiled Unit Component "
                        "with the %s Profile ID"
                    )
                    % parent_hier
                )

            seq = (
                env["bldg.prof"].search_count(
                    [
                        ("unit_id", "=", unit.id),
                        ("profile_level", "=", "unit_sub_component"),
                    ]
                )
                + 1
            )
            new_id = f"{unit_hier}{parent_hier[48:58]}{seq:02}"

        if new_id:
            vals["hierarchical_id"] = new_id
        return vals

    # ---------------------------------------------------------------------
    # CRUD HOOKS – unchanged
    # ---------------------------------------------------------------------
    @api.model
    def create(self, vals):
        """
        1.  Confirm/lock older open profile
        2.  Compute hierarchical_id
        3.  Auto-create attribute rows from templates
        """
        level = vals.get("profile_level")
        if not level:
            return super().create(vals)

        # -----------------------------------------------------
        # 1.  Lock/confirmation logic
        # -----------------------------------------------------
        domain = [("profile_level", "=", level), ("locked", "=", False)]
        if level == "building_complex":
            domain.append(("group_id", "=", vals.get("group_id")))
        elif level == "building":
            domain.append(("building_id", "=", vals.get("building_id")))
        elif level == "floor":
            domain.append(("floor_id", "=", vals.get("floor_id")))
        elif level in ("unit", "unit_component", "unit_sub_component"):
            domain.append(("unit_id", "=", vals.get("unit_id")))
        else:
            return super().create(vals)

        existing = self.search(domain, limit=1)
        if existing and not self.env.context.get("skip_profile_lock_confirm"):
            entity_name = (
                existing.group_id.name
                if level == "building_complex"
                else (
                    existing.building_id.name
                    if level == "building"
                    else (
                        existing.floor_id.name
                        if level == "floor"
                        else existing.unit_id.name
                    )
                )
            )
            level_label = dict(LEVELS).get(level, level)
            raise ValidationError(
                _(
                    "You are about to create a new profile for {entity} ({level}).\n"
                    "This {level} already has an open profile ({old_profile}).\n"
                    "If you create a new profile, the open profile will be locked "
                    "and no longer editable.\n\n"
                    "Are you sure you want to create a new profile?\n\n"
                    "Please call create() again with context key "
                    "'skip_profile_lock_confirm' = True to confirm."
                ).format(
                    entity=entity_name,
                    level=level_label,
                    old_profile=existing.display_name,
                )
                + "\n\n[skip_profile_lock_confirm]"
            )

        existing.write({"locked": True})

        # -----------------------------------------------------
        # 2.  Generate hierarchical_id
        # -----------------------------------------------------
        vals = self._compute_hierarchical_id(vals)

        # -----------------------------------------------------
        # 3.  Create the profile
        # -----------------------------------------------------
        profile = super().create(vals)
        # -----------------------------------------------------
        # 4.  Create the profile
        # -----------------------------------------------------
        attributes = self.env["bldg.attr"].search(
            [("profile_level", "=", profile.profile_level)]
        )
        profile.write(
            {
                "attribute_line_ids": [
                    (0, 0, {"attribute_id": attr.id}) for attr in attributes
                ]
            }
        )
        # -----------------------------------------------------
        # 5. Auto-create propagated attribute-lines
        # -----------------------------------------------------
        propagated_attrs = self.env["bldg.attr"].search(
            [
                (
                    "profile_level",
                    "in",
                    [
                        "building_complex",
                        "building",
                        "floor",
                        "unit",
                        "unit_component",
                        "unit_sub_component",
                    ],
                ),
                ("inheritance_type", "=", "propagated"),
            ]
        )
        deeper_level_order = {
            "building_complex": 1,
            "building": 2,
            "floor": 3,
            "unit": 4,
            "unit_component": 5,
            "unit_sub_component": 6,
        }
        current_order = deeper_level_order[profile.profile_level]
        attrs_to_create = propagated_attrs.filtered(
            lambda a: deeper_level_order[a.profile_level] < current_order
        )
        if attrs_to_create:
            profile.write(
                {
                    "attribute_line_ids": [
                        (0, 0, {"attribute_id": attr.id}) for attr in attrs_to_create
                    ]
                }
            )

        # -----------------------------------------------------
        # 6.  RETURN the newly created record
        # -----------------------------------------------------
        return profile

    # ------------------------------------------------------------------
    # Re-sync attribute lines when profile level changes
    # ------------------------------------------------------------------
    @api.onchange("profile_level")
    def _onchange_level_rebuild_attrs(self):
        if self.id and self.attribute_line_ids:
            raise ValidationError(
                _(
                    "Changing the profile level will delete existing attribute lines "
                    "and create new ones matching the new level. Save to confirm."
                )
            )

    def write(self, vals):
        if "profile_level" in vals:
            for prof in self:
                # 1. remove old lines
                prof.attribute_line_ids.unlink()
                # 2. add lines for new level
                new_attrs = self.env["bldg.attr"].search(
                    [("profile_level", "=", vals["profile_level"])]
                )
                for attr in new_attrs:
                    self.env["bldg.profile.attribute.line"].create(
                        {
                            "profile_id": prof.id,
                            "attribute_id": attr.id,
                        }
                    )
        return super().write(vals)
