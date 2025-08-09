from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgAttrFloatScoringRule(models.Model):
    _name = "bldg.attr.float.scoring.rule"
    _description = _("Scoring Rules for Float Attributes")
    _order = "attribute_id, range_min"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "range_sanity",
            "CHECK (range_max > range_min)",
            _("Maximum must be greater than minimum."),
        ),
        (
            "no_float_overlap",
            "EXCLUDE USING gist (attribute_id WITH =, "
            "numrange(range_min, range_max, '[)') WITH &&)",
            _("Float ranges must not overlap."),
        ),
    ]
    # ==============================================================================
    # FIELDS
    # ==============================================================================
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
        domain=[("data_type", "=", "float")],
    )
    range_min = fields.Float(string=_("Range Minimum"), digits=(12, 2))
    range_max = fields.Float(string=_("Range Maximum"), digits=(12, 2))
    points = fields.Float(string=_("Points"), required=True)

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ==============================================================================
    # METHODS
    # ==============================================================================
    @api.depends("attribute_id", "range_min", "range_max")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.attribute_id.name or _('(No attribute)')}: "
                f"{rec.range_min:.2f} – {rec.range_max:.2f}"
            )

    @api.constrains("range_min", "range_max")
    def _check_range(self):
        for rec in self:
            if rec.range_min is None or rec.range_max is None:
                raise ValidationError(_("Both range_min and range_max are required."))

    @api.model
    def match_rule(self, attribute_record, value):
        if (
            value is None
            or not attribute_record
            or attribute_record.data_type != "float"
        ):
            return None
        return self.search(
            [
                ("attribute_id", "=", attribute_record.id),
                ("range_min", "<=", value),
                ("range_max", ">", value),
                ("active", "=", True),
            ],
            limit=1,
        )

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
