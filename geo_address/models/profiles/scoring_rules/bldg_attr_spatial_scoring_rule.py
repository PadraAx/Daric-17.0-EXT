# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgAttrSpatialScoringRule(models.Model):
    _name = "bldg.attr.spatial.scoring.rule"
    _description = _("Scoring Rules for Spatial Attributes")
    _order = "attribute_id, coord_type, sequence"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "unique_attr_coord_seq",
            "unique(attribute_id, coord_type, sequence)",
            _("Sequence must be unique per attribute and coordinate type."),
        ),
    ]

    # ------------------------------------------------------------------
    # CORE FIELDS
    # ------------------------------------------------------------------
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )
    code = fields.Char(
        string="Code",
        compute="_compute_code",
        store=True,
        readonly=True,
        index=True,
        help="Auto-generated code based on attribute and rule sequence",
    )

    attribute_id = fields.Many2one(
        "bldg.attr",
        required=True,
        ondelete="cascade",
        domain=[("data_type", "=", "spatial")],
    )

    coord_type = fields.Selection(
        [
            ("longitude", "Longitude"),
            ("latitude", "Latitude"),
            ("height", "Altitude (Above Reference)"),
            ("depth", "Depth (Below Reference)"),
        ],
        required=True,
    )

    sequence = fields.Integer(default=10)

    precision = fields.Integer(
        string="Decimal Places",
        default=6,
        help="Only used for Longitude and Latitude.",
    )

    uom_category_id = fields.Many2one(
        "uom.category",
        string="UoM Category",
        default=lambda self: self.env.ref("uom.uom_categ_length"),
    )

    uom_id = fields.Many2one(
        "uom.uom",
        string="Unit",
        domain="[('category_id', '=', uom_category_id)]",
    )

    range_min = fields.Float("Range Min")
    range_max = fields.Float("Range Max")
    points = fields.Float("Points", required=True)

    surface_reference = fields.Char(
        string="Surface Reference",
        help="Reference surface or datum (e.g., sea level, street level, tunnel base).",
    )

    depth_category = fields.Selection(
        [
            ("utility", "Utility Infrastructure"),
            ("transport", "Transport"),
            ("defense", "Defense"),
            ("natural", "Natural Feature"),
            ("other", "Other"),
        ],
        string="Depth Category",
    )

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ------------------------------------------------------------------
    # COMPUTED
    # ------------------------------------------------------------------
    @api.depends("attribute_id", "coord_type", "range_min", "range_max")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.attribute_id.name or _('(No attribute)')}: "
                f"{rec.coord_type} {rec.range_min:.2f} – {rec.range_max:.2f}"
            )

    # ------------------------------------------------------------------
    # CONSTRAINTS
    # ------------------------------------------------------------------
    @api.constrains("range_min", "range_max")
    def _check_range(self):
        for rec in self:
            if (
                rec.range_min is not None
                and rec.range_max is not None
                and rec.range_min >= rec.range_max
            ):
                raise ValidationError(_("Range max must be greater than min."))

    @api.constrains("coord_type", "precision")
    def _check_precision(self):
        for rec in self:
            if rec.coord_type in ("longitude", "latitude") and rec.precision < 0:
                raise ValidationError(_("Precision must be non-negative."))

    @api.constrains("coord_type", "uom_id")
    def _check_uom_id(self):
        for rec in self:
            if rec.coord_type in ("height", "depth") and not rec.uom_id:
                raise ValidationError(
                    _("A unit of measure must be defined for height/depth.")
                )

    # ------------------------------------------------------------------
    # BUSINESS API
    # ------------------------------------------------------------------
    @api.model
    def match_rule(self, attribute_record, coord_dict):
        """
        Return the first rule that matches any coordinate in `coord_dict`.

        coord_dict format:
            {
                'longitude': float,
                'latitude':  float,
                'height':    float,
                'depth':     float,
            }
        Only keys present in the dict are evaluated.
        """
        if not isinstance(coord_dict, dict):
            return None
        if not attribute_record or attribute_record.data_type != "spatial":
            return None

        for key, val in coord_dict.items():
            if val is None:
                continue
            rule = self.search(
                [
                    ("attribute_id", "=", attribute_record.id),
                    ("coord_type", "=", key),
                    ("range_min", "<=", val),
                    ("range_max", ">", val),
                    ("active", "=", True),
                ],
                limit=1,
            )
            if rule:
                return rule
        return None

    @api.depends("attribute_id")
    def _compute_code(self):
        for rec in self:
            if not rec.attribute_id or not rec.attribute_id.code:
                rec.code = False
                continue

            # Get all rules under this attribute (current model only), ordered by id
            sibling_rules = self.search(
                [("attribute_id", "=", rec.attribute_id.id)], order="id"
            )

            # Determine index of this record among siblings
            index = 0
            for i, rule in enumerate(sibling_rules):
                if rule.id == rec.id:
                    index = i
                    break

            rec.code = f"{rec.attribute_id.code}{str(index + 1).zfill(2)}"
