# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
import re

LEVELS = [
    ("building_complex", "Building Complex"),
    ("building", "Building"),
    ("floor", "Floor"),
    ("unit", "Unit"),
    ("unit_component", "Unit Component"),
    ("unit_sub_component", "Unit Sub-Component"),
]


class BldgAttribute(models.Model):
    _name = "bldg.attr"
    _description = _("Building Attributes")
    _order = "sequence, id"
    _sql_constraints = [
        (
            "name_level_unique",
            "UNIQUE(name, profile_level)",
            _(
                "An attribute with this name already exists for the given profile level."
            ),
        ),
    ]
    # ==============================================================================
    # FIELDS
    # ==============================================================================
    # ------------------------------------------------------------------
    # CORE ATTRIBUTE DEFINITION
    # ------------------------------------------------------------------
    name = fields.Char(required=True, index=True)
    description = fields.Html(sanitize=True, strip_style=True, prefetch=False)
    sequence = fields.Integer(default=10)
    code = fields.Char(
        string="Code",
        compute="_compute_code",
        store=True,
        readonly=True,
        index=True,
        help="Auto-generated code from attr_type, inheritance_type, data_type, and computation_type",
    )

    profile_level = fields.Selection(
        LEVELS, string=_("Profile Level"), required=True, index=True
    )
    attr_type = fields.Selection(
        [
            ("physical", _("Physical")),
            ("architectural", _("Architectural")),
            ("legal", _("Legal")),
        ],
        required=True,
        index=True,
    )
    # ---------------------------------------------------------------
    # INHERITANCE
    # ---------------------------------------------------------------
    inheritance_type = fields.Selection(
        [
            ("non_inheritable", "Non-inheritable"),
            ("propagated", "Propagated"),
        ],
        string="Impact on next levels",
        default="non_inheritable",
        required=True,
    )
    # ---------------------------------------------------------------
    # DATA-TYPE–SPECIFIC
    # ---------------------------------------------------------------
    data_type = fields.Selection(
        [
            ("selection", _("Selection")),
            ("boolean", _("Boolean")),
            ("integer", _("Integer")),
            ("float", _("Float")),
            ("spatial", _("Spatial")),
            ("string", _("String")),
            ("color", _("Color")),
            ("document", _("Document Group")),
        ],
        required=True,
        index=True,
    )
    boolean_scoring_ids = fields.One2many(
        "bldg.attr.boolean.scoring.rule", "attribute_id", string="Boolean Scoring Rules"
    )
    color_scoring_ids = fields.One2many(
        "bldg.attr.color.scoring.rule", "attribute_id", string="Color Scoring Rules"
    )
    document_scoring_ids = fields.One2many(
        "bldg.attr.document.scoring.rule",
        "attribute_id",
        string="Document Scoring Rules",
    )
    float_scoring_ids = fields.One2many(
        "bldg.attr.float.scoring.rule", "attribute_id", string="Float Scoring Rules"
    )
    integer_scoring_ids = fields.One2many(
        "bldg.attr.integer.scoring.rule", "attribute_id", string="Integer Scoring Rules"
    )
    selection_scoring_ids = fields.One2many(
        "bldg.attr.selection.scoring.rule",
        "attribute_id",
        string="Selection Scoring Rules",
    )
    spatial_scoring_ids = fields.One2many(
        "bldg.attr.spatial.scoring.rule", "attribute_id", string="Spatial Scoring Rules"
    )
    string_scoring_ids = fields.One2many(
        "bldg.attr.string.scoring.rule", "attribute_id", string="String Scoring Rules"
    )
    uom_category_id = fields.Many2one(
        "uom.category",
        string="UoM Category",
        help="Required for numeric data types.",
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit",
        domain="[('category_id', '=', uom_category_id)]",
    )

    # ------------------------------------------------------------------
    # COMPUTATION
    # ------------------------------------------------------------------
    computation_type = fields.Selection(
        [("manual", "Manual"), ("formula", "Formula driven")],
        string="Computation Type",
        default="manual",
        required=True,
    )
    root_calc_group_id = fields.Many2one(
        "bldg.calc.group", string="Root Expression", ondelete="set null", index=True
    )

    # ==============================================================================
    # METHODS
    # ==============================================================================
    # ------------------------------------------------------------------
    # CONSTRAINTS
    # ------------------------------------------------------------------
    @api.constrains("data_type", "uom_category_id")
    def _check_uom_category(self):
        for rec in self:
            if rec.data_type in ("integer", "float") and not rec.uom_category_id:
                raise ValidationError(
                    _("Numeric attributes must specify a UoM category.")
                )

    @api.constrains("uom_id", "uom_category_id")
    def _check_uom_category_match(self):
        for rec in self:
            if (
                rec.uom_id
                and rec.uom_category_id
                and rec.uom_id.category_id != rec.uom_category_id
            ):
                raise ValidationError(
                    _("Default UoM must belong to the selected UoM category.")
                )

    @api.constrains("profile_level", "inheritance_type")
    def _check_level_six_rule(self):
        for rec in self:
            if (
                rec.profile_level == "unit_sub_component"
                and rec.inheritance_type != "non_inheritable"
            ):
                raise ValidationError(
                    _(
                        "Level 6 (Unit Sub-Component) attributes can only be non-inheritable."
                    )
                )

    # ------------------------------------------------------------------
    # ONCHANGE / HELPERS
    # ------------------------------------------------------------------
    @api.onchange("profile_level")
    def _onchange_profile_level_inheritance(self):
        if self.profile_level == "unit_sub_component":
            self.inheritance_type = "non_inheritable"

    def _get_formula_symbols(self):
        """Return a dict {symbol: parameter_id} for all operands."""
        self.ensure_one()
        return {op.operand_name: op.parameter_id for op in self.operand_ids}

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for attr in records:
            # Assign to existing profiles of the same level
            if attr.profile_level:
                profiles = self.env["bldg.prof"].search(
                    [("profile_level", "=", attr.profile_level)]
                )
                for prof in profiles:
                    if not prof.attribute_line_ids.filtered(
                        lambda l: l.attribute_id == attr
                    ):
                        self.env["bldg.profile.attribute.line"].create(
                            {
                                "profile_id": prof.id,
                                "attribute_id": attr.id,
                            }
                        )

            # Propagate down if needed
            attr._propagate_to_lower_levels()

            # Create / delete boolean scoring rules
            if attr.data_type == "boolean":
                self.env["bldg.score"].create_boolean_rules(attr)
            else:
                self.env["bldg.score"].unlink_boolean_rules(attr)

            # 🔄 Ensure root calculation group if computation_type is 'formula'
            if attr.computation_type == "formula":
                attr._ensure_root_calc_group()

        return records

    # ------------------------------------------------------------------
    # WRITE
    # ------------------------------------------------------------------
    def write(self, vals):
        res = super().write(vals)

        for attr in self:
            # If computation_type changed:
            if "computation_type" in vals:
                if vals["computation_type"] == "formula":
                    attr._ensure_root_calc_group()
                else:
                    attr._ensure_no_calc_groups()

            # Create / delete boolean scoring rules on data_type change
            if "data_type" in vals:
                if attr.data_type == "boolean":
                    self.env["bldg.score"].create_boolean_rules(attr)
                else:
                    self.env["bldg.score"].unlink_boolean_rules(attr)

            # propagate down on inheritance_type change
            if vals.get("inheritance_type") == "propagated":
                attr._propagate_to_lower_levels()

        return res

    # ------------------------------------------------------------------
    # INTERNAL PROPAGATION LOGIC
    # ------------------------------------------------------------------
    def _propagate_to_lower_levels(self):
        self.ensure_one()
        if self.inheritance_type != "propagated":
            return

        ordered_levels = [lvl[0] for lvl in LEVELS]
        try:
            start_idx = ordered_levels.index(self.profile_level)
        except ValueError:
            return

        lower_levels = ordered_levels[start_idx + 1 :]
        for lvl in lower_levels:
            if self.search_count(
                [
                    ("name", "=", self.name),
                    ("profile_level", "=", lvl),
                    ("inheritance_type", "=", "non_inheritable"),
                ]
            ):
                continue
            self.copy(
                default={
                    "profile_level": lvl,
                    "inheritance_type": "non_inheritable",
                }
            )

    @api.depends("attr_type", "inheritance_type", "data_type", "computation_type")
    def _compute_code(self):
        attr_type_map = {
            "physical": "PH",
            "architectural": "AR",
            "legal": "LG",
        }
        inheritance_type_map = {
            "non_inheritable": "NI",
            "propagated": "PR",
        }
        data_type_map = {
            "selection": "SE",
            "boolean": "BO",
            "integer": "IN",
            "float": "FL",
            "spatial": "SP",
            "string": "ST",
            "color": "CO",
            "document_group": "DG",
        }
        computation_type_map = {
            "manual": "MA",
            "formula": "FO",
        }

        for rec in self:
            at = attr_type_map.get(rec.attr_type or "", "XX")
            inh = inheritance_type_map.get(rec.inheritance_type or "", "XX")
            dt = data_type_map.get(rec.data_type or "", "XX")
            comp = computation_type_map.get(rec.computation_type or "", "XX")
            rec.code = f"{at}{inh}{dt}{comp}"

    # ------------------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------------------
    def name_get(self):
        return [(rec.id, f"{rec.code or ''} {rec.name or ''}".strip()) for rec in self]

    # ------------------------------------------------------------------
    # ROOT CALC GROUP AUTO-MAINTENANCE
    # ------------------------------------------------------------------
    def _ensure_root_calc_group(self):
        CalcGroup = self.env["bldg.calc.group"]
        for attr in self:
            if attr.computation_type != "formula":
                continue

            existing = CalcGroup.search(
                [
                    ("target_param_id", "=", attr.id),
                    ("parent_id", "=", False),
                ]
            )
            if not existing:
                CalcGroup.create(
                    {
                        "target_param_id": attr.id,
                        "operator": "+",
                        "sequence": 10,
                    }
                )
            elif len(existing) > 1:
                raise ValidationError(
                    _("Attribute '%s' has more than one root calculation group.")
                    % attr.name
                )

    def _ensure_no_calc_groups(self):
        CalcGroup = self.env["bldg.calc.group"]
        for attr in self:
            groups = CalcGroup.search([("target_param_id", "=", attr.id)])
            groups.unlink()
