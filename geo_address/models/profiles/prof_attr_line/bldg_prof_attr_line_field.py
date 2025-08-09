# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class BuildingProfileAttributeLine(models.Model):
    _name = "bldg.profile.attribute.line"
    _description = "Profile-specific Attribute Line"
    _order = "attribute_id"

    _sql_constraints = [
        (
            "profile_attribute_unique",
            "UNIQUE(profile_id, attribute_id)",
            _("This attribute already exists on the profile."),
        )
    ]

    # ------------------------------------------------------------------
    # RELATION: PROFILE (bldg.prof)
    # ------------------------------------------------------------------
    profile_id = fields.Many2one(
        "bldg.prof",
        required=True,
        ondelete="cascade",
        index=True,
    )
    profile_hierarchical_id = fields.Char(
        related="profile_id.hierarchical_id", store=True, readonly=True
    )
    prof_profile_level = fields.Selection(
        related="profile_id.profile_level", store=True, readonly=True
    )

    # ------------------------------------------------------------------
    # RELATION: ATTRIBUTE (bldg.attr)
    # ------------------------------------------------------------------
    attribute_id = fields.Many2one(
        "bldg.attr",
        required=True,
        ondelete="cascade",
        index=True,
    )
    attribute_name = fields.Char(related="attribute_id.name", store=True, readonly=True)
    attr_profile_level = fields.Selection(
        related="attribute_id.profile_level", store=True, readonly=True
    )
    attr_type = fields.Selection(
        related="attribute_id.attr_type", store=True, readonly=True
    )
    inheritance_type = fields.Selection(
        related="attribute_id.inheritance_type", store=True, readonly=True
    )
    data_type = fields.Selection(
        related="attribute_id.data_type", store=True, readonly=True
    )
    computation_type = fields.Selection(
        related="attribute_id.computation_type", store=True, readonly=True
    )
    uom_category_id = fields.Many2one(
        related="attribute_id.uom_category_id", store=True, readonly=True
    )
    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit",
        related="attribute_id.uom_id",
        store=True,
        readonly=True,
    )

    # ------------------------------------------------------------------
    # RELATION: SCORING RULES (bldg.attr.*.scoring.rule)
    # ------------------------------------------------------------------

    # Boolean
    boolean_score_id = fields.Many2one(
        "bldg.attr.boolean.scoring.rule",
        string="Boolean Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    boolean_score_code = fields.Char(
        related="boolean_score_id.code", store=True, readonly=True
    )
    boolean_points = fields.Float(
        string="Boolean Points",
        related="boolean_score_id.points",
        store=True,
        readonly=True,
    )

    # Color
    color_score_id = fields.Many2one(
        "bldg.attr.color.scoring.rule",
        string="Color Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    color_score_code = fields.Char(
        related="color_score_id.code", store=True, readonly=True
    )
    color_points = fields.Float(
        string="Color Points",
        related="color_score_id.points",
        store=True,
        readonly=True,
    )

    # Document
    document_score_id = fields.Many2one(
        "bldg.attr.document.scoring.rule",
        string="Document Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    document_score_code = fields.Char(
        related="document_score_id.code", store=True, readonly=True
    )
    document_points = fields.Float(
        string="Document Points",
        related="document_score_id.points",
        store=True,
        readonly=True,
    )

    # Float
    float_score_id = fields.Many2one(
        "bldg.attr.float.scoring.rule",
        string="Float Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    float_score_code = fields.Char(
        related="float_score_id.code", store=True, readonly=True
    )
    float_points = fields.Float(
        string="Float Points",
        related="float_score_id.points",
        store=True,
        readonly=True,
    )

    # Integer
    integer_score_id = fields.Many2one(
        "bldg.attr.integer.scoring.rule",
        string="Integer Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    integer_score_code = fields.Char(
        related="integer_score_id.code", store=True, readonly=True
    )
    integer_points = fields.Float(
        string="Integer Points",
        related="integer_score_id.points",
        store=True,
        readonly=True,
    )

    # Selection
    selection_score_id = fields.Many2one(
        "bldg.attr.selection.scoring.rule",
        string="Selection Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    selection_score_code = fields.Char(
        related="selection_score_id.code", store=True, readonly=True
    )
    selection_points = fields.Float(
        string="Selection Points",
        related="selection_score_id.points",
        store=True,
        readonly=True,
    )

    # Spatial
    spatial_score_id = fields.Many2one(
        "bldg.attr.spatial.scoring.rule",
        string="Spatial Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    spatial_score_code = fields.Char(
        related="spatial_score_id.code", store=True, readonly=True
    )
    spatial_points = fields.Float(
        string="Spatial Points",
        related="spatial_score_id.points",
        store=True,
        readonly=True,
    )

    # String
    string_score_id = fields.Many2one(
        "bldg.attr.string.scoring.rule",
        string="String Scoring Rule",
        domain=lambda self: [("attribute_id", "=", self.attribute_id.id)],
    )
    string_score_code = fields.Char(
        related="string_score_id.code", store=True, readonly=True
    )
    string_points = fields.Float(
        string="String Points",
        related="string_score_id.points",
        store=True,
        readonly=True,
    )

    # ------------------------------------------------------------------
    # DERIVED / COMPUTED SCORING RESULT
    # ------------------------------------------------------------------
    points = fields.Float(
        string="Points",
        compute="_compute_points",
        store=True,
        readonly=True,
        help="Final point derived from selected scoring rule (based on data_type)",
    )

    # ------------------------------------------------------------------
    # VALUES: RAW, COMPUTED, FORMATTED
    # ------------------------------------------------------------------
    value_integer_raw = fields.Integer()
    value_float_raw = fields.Float()

    value_integer = fields.Integer(
        compute="_compute_value_integer",
        inverse="_inverse_value_integer",
        store=True,
    )
    value_float = fields.Float(
        compute="_compute_value_float",
        inverse="_inverse_value_float",
        store=True,
    )
    formula_value = fields.Float(
        string="Formula Value",
        compute="_compute_formula_value",
        store=True,
        help="Value calculated via formula from related calculation group.",
    )

    value_in_reference_uom = fields.Float(
        string="Value (reference unit)",
        digits="Product Unit of Measure",
        compute="_compute_value_in_reference_uom",
        store=True,
        readonly=True,
    )
    value_display = fields.Char(compute="_compute_value_display", store=False)

    # ------------------------------------------------------------------
    # DOCUMENT ATTACHMENT (ir.attachment)
    # ------------------------------------------------------------------
    document_id = fields.Many2one(
        "ir.attachment",
        string="Attached Document",
        ondelete="cascade",
        domain="[('res_model', '=', 'bldg.profile.attribute.line')]",
    )

    # ------------------------------------------------------------------
    # UI STATE / FLAGS
    # ------------------------------------------------------------------
    is_editable = fields.Boolean(compute="_compute_editable_flags", store=False)

    # ------------------------------------------------------------------
    # ADDITIONAL / DEBUGGING
    # ------------------------------------------------------------------
    debug_info = fields.Char(
        string="Debug Info",
        compute="_compute_debug_info",
        store=False,
    )
    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        compute="_compute_hierarchical_id",
        store=True,
    )

    # ==============================================================================
    # METHODS
    # ==============================================================================
    # ------------------------------------------------------------------
    # SQL / PYTHON CONSTRAINTS
    # ------------------------------------------------------------------

    @api.constrains(
        "data_type",
        "boolean_score_id",
        "color_score_id",
        "document_score_id",
        "float_score_id",
        "integer_score_id",
        "selection_score_id",
        "spatial_score_id",
        "string_score_id",
    )
    def _check_required_scoring_rule(self):
        """Ensure a scoring rule is chosen for the attribute's data-type."""
        for rec in self:
            missing = {
                "boolean": not rec.boolean_score_id,
                "color": not rec.color_score_id,
                "document": not rec.document_score_id,
                "float": not rec.float_score_id,
                "integer": not rec.integer_score_id,
                "selection": not rec.selection_score_id,
                "spatial": not rec.spatial_score_id,
                "string": not rec.string_score_id,
            }.get(rec.data_type)
            if missing:
                raise ValidationError(
                    _("%s scoring rule must be set when data type is '%s'.")
                    % (rec.data_type.capitalize(), rec.data_type)
                )

    @api.constrains(
        "value_integer_raw",
        "value_float_raw",
        "boolean_score_id",
        "selection_score_id",
        "string_score_id",
        "color_score_id",
        "document_score_id",
        "spatial_score_id",
    )
    def _check_single_value(self):
        """Exactly one value field must be populated, matching the data type."""
        for rec in self:
            value_map = {
                "selection": rec.selection_score_id,
                "boolean": rec.boolean_score_id,
                "integer": rec.value_integer_raw,
                "float": rec.value_float_raw,
                "string": rec.string_score_id,
                "color": rec.color_score_id,
                "document": rec.document_score_id,
                "spatial": rec.spatial_score_id,
            }

            value = value_map.get(rec.data_type)
            if value in (None, False, "", 0, 0.0):
                raise ValidationError(
                    _("A value must be set for attribute '%s' with data type '%s'.")
                    % (rec.attribute_id.name, rec.data_type)
                )

            # Ensure no other fields contain data
            non_empty = [
                k for k, v in value_map.items() if v not in (None, False, "", 0, 0.0)
            ]
            if len(non_empty) > 1:
                raise ValidationError(
                    _(
                        "Only one value should be filled for attribute '%s'. "
                        "Conflicts in: %s"
                    )
                    % (rec.attribute_id.name, ", ".join(non_empty))
                )

    @api.constrains("data_type", "document_score_id", "document_id")
    def _check_document_attachment_allowed(self):
        for rec in self:
            if (
                rec.data_type == "document"
                and rec.document_id
                and not rec.document_score_id
            ):
                raise ValidationError(
                    _(
                        "You can only attach a document when a Document scoring rule "
                        "is selected."
                    )
                )

    # ------------------------------------------------------------------
    # COMPUTE: POINTS (numeric score)
    # ------------------------------------------------------------------

    @api.depends(
        "boolean_score_id.points",
        "color_score_id.points",
        "document_score_id.points",
        "float_score_id.points",
        "integer_score_id.points",
        "selection_score_id.points",
        "spatial_score_id.points",
        "string_score_id.points",
        "data_type",
    )
    def _compute_points(self):
        """Take the points from the scoring rule that matches data_type."""
        for rec in self:
            rec.points = {
                "boolean": rec.boolean_score_id.points,
                "color": rec.color_score_id.points,
                "document": rec.document_score_id.points,
                "float": rec.float_score_id.points,
                "integer": rec.integer_score_id.points,
                "selection": rec.selection_score_id.points,
                "spatial": rec.spatial_score_id.points,
                "string": rec.string_score_id.points,
            }.get(rec.data_type, 0.0) or 0.0

    @api.depends("attribute_id")
    def _compute_formula_value(self):
        for line in self:
            formula_group = self.env["bldg.calc.group"].search(
                [("target_param_id", "=", line.attribute_id.id)], limit=1
            )

            if formula_group:
                line.formula_value = formula_group.target_param_value
            else:
                line.formula_value = 0.0

    # ------------------------------------------------------------------
    # COMPUTE / INVERSE: INTEGER VALUE
    # ------------------------------------------------------------------

    @api.depends(
        "profile_id.parent_id",
        "inheritance_type",
        "attribute_id",
        "value_integer_raw",
        "attribute_id.computation_type",
    )
    def _compute_value_integer(self):
        for line in self:
            attr = line.attribute_id
            if attr.computation_type == "formula":
                continue
            if attr.inheritance_type == "propagated" and line.profile_id.parent_id:
                parent_line = self.search(
                    [
                        ("profile_id", "=", line.profile_id.parent_id.id),
                        ("attribute_id", "=", attr.id),
                    ],
                    limit=1,
                )
                line.value_integer = parent_line.value_integer if parent_line else 0
            else:
                line.value_integer = line.value_integer_raw

    def _inverse_value_integer(self):
        for line in self:
            if line.inheritance_type != "propagated":
                line.value_integer_raw = line.value_integer

    # ------------------------------------------------------------------
    # COMPUTE / INVERSE: FLOAT VALUE
    # ------------------------------------------------------------------

    @api.depends(
        "profile_id.parent_id",
        "inheritance_type",
        "attribute_id",
        "value_float_raw",
        "attribute_id.computation_type",
    )
    def _compute_value_float(self):
        for line in self:
            attr = line.attribute_id
            if attr.computation_type == "formula":
                continue
            if attr.inheritance_type == "propagated" and line.profile_id.parent_id:
                parent_line = self.search(
                    [
                        ("profile_id", "=", line.profile_id.parent_id.id),
                        ("attribute_id", "=", attr.id),
                    ],
                    limit=1,
                )
                line.value_float = parent_line.value_float if parent_line else 0.0
            else:
                line.value_float = line.value_float_raw

    def _inverse_value_float(self):
        for line in self:
            if line.inheritance_type != "propagated":
                line.value_float_raw = line.value_float

    # ------------------------------------------------------------------
    # COMPUTE: FORMULA RESULT
    # ------------------------------------------------------------------

    @api.depends(
        "value_integer_raw",
        "value_float_raw",
        "attribute_id.uom_id",
        "attribute_id.computation_type",
        "attribute_id.root_calc_group_id",
    )
    def _compute_value_in_reference_uom(self):
        for line in self:
            attr = line.attribute_id
            if attr.computation_type == "manual":
                raw = 0.0
                if attr.data_type == "integer":
                    raw = float(line.value_integer_raw or 0)
                elif attr.data_type == "float":
                    raw = float(line.value_float_raw or 0.0)

                if attr.uom_id:
                    line.value_in_reference_uom = attr.uom_id._compute_quantity(
                        raw, attr.uom_id, rounding_method="HALF-UP"
                    )
                else:
                    line.value_in_reference_uom = raw

            elif attr.computation_type == "formula" and attr.root_calc_group_id:
                line.value_in_reference_uom = attr.root_calc_group_id.evaluate(
                    record=line.profile_id
                )

            else:
                line.value_in_reference_uom = 0.0

    # ------------------------------------------------------------------
    # COMPUTE: HUMAN-READABLE DISPLAY VALUE
    # ------------------------------------------------------------------

    @api.depends(
        "selection_score_id.name",
        "boolean_score_id.name",
        "value_integer",
        "value_float",
        "string_score_id.name",
        "color_score_id.name",
        "document_score_id.name",
        "spatial_score_id.name",
        "data_type",
    )
    def _compute_value_display(self):
        for rec in self:
            dt = rec.data_type
            rec.value_display = {
                "selection": rec.selection_score_id.name or "",
                "boolean": rec.boolean_score_id.name or "",
                "integer": (
                    str(rec.value_integer) if rec.value_integer is not None else ""
                ),
                "float": str(rec.value_float) if rec.value_float is not None else "",
                "string": rec.string_score_id.name or "",
                "color": rec.color_score_id.name or "",
                "document": rec.document_score_id.name or "",
                "spatial": rec.spatial_score_id.name or "",
            }.get(dt, "")

    # ------------------------------------------------------------------
    # COMPUTE: EDITABLE FLAG
    # ------------------------------------------------------------------

    @api.depends("inheritance_type", "computation_type")
    def _compute_editable_flags(self):
        for rec in self:
            rec.is_editable = (
                rec.inheritance_type != "propagated"
                and rec.computation_type == "manual"
            )

    # ------------------------------------------------------------------
    # COMPUTE: HIERARCHICAL ID
    # ------------------------------------------------------------------

    @api.depends(
        "profile_hierarchical_id",
        "data_type",
        "boolean_score_code",
        "color_score_code",
        "document_score_code",
        "float_score_code",
        "integer_score_code",
        "selection_score_code",
        "spatial_score_code",
        "string_score_code",
    )
    def _compute_hierarchical_id(self):
        for rec in self:
            score_code = {
                "boolean": rec.boolean_score_code,
                "color": rec.color_score_code,
                "document": rec.document_score_code,
                "float": rec.float_score_code,
                "integer": rec.integer_score_code,
                "selection": rec.selection_score_code,
                "spatial": rec.spatial_score_code,
                "string": rec.string_score_code,
            }.get(rec.data_type, "") or ""
            rec.hierarchical_id = (rec.profile_hierarchical_id or "") + score_code

    # ------------------------------------------------------------------
    # COMPUTE: DEBUG INFO
    # ------------------------------------------------------------------

    @api.depends(
        "data_type",
        "computation_type",
        "inheritance_type",
        "value_integer_raw",
        "value_float_raw",
        "value_integer",
        "value_float",
        "value_in_reference_uom",
    )
    def _compute_debug_info(self):
        for rec in self:
            rec.debug_info = (
                f"Type: {rec.data_type} | "
                f"Comp: {rec.computation_type} | "
                f"Inherit: {rec.inheritance_type} | "
                f"Raw: {rec.value_integer_raw}/{rec.value_float_raw} | "
                f"Computed: {rec.value_integer}/{rec.value_float} | "
                f"Ref UOM: {rec.value_in_reference_uom}"
            )

    # ------------------------------------------------------------------
    # HELPER (unused, optional)
    # ------------------------------------------------------------------

    def _get_manual_numeric_raw(self):
        """Return the numeric value entered by the user in manual mode."""
        self.ensure_one()
        if self.data_type == "integer":
            return float(self.value_integer_raw or 0)
        if self.data_type == "float":
            return float(self.value_float_raw or 0)
        return 0.0
