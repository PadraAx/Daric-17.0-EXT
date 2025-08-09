from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgAttrBooleanScoringRule(models.Model):
    _name = "bldg.attr.boolean.scoring.rule"
    _description = _("Scoring Rules for Boolean Attributes")
    _order = "attribute_id"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "boolean_unique",
            "UNIQUE(attribute_id)",
            _("Only one Boolean rule pair (TRUE / FALSE) is allowed per attribute."),
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
        domain=[("data_type", "=", "boolean")],
    )

    points_if_true = fields.Float(string=_("Points when TRUE"), default=0.0)
    points_if_false = fields.Float(string=_("Points when FALSE"), default=0.0)

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ==============================================================================
    # METHODS
    # ==============================================================================
    @api.depends("attribute_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.attribute_id.name or _('(No attribute)')}: BOOL"

    def get_points(self, value):
        """Return points for the given boolean value."""
        self.ensure_one()
        return self.points_if_true if value else self.points_if_false

    @api.model
    def match_rule(self, attribute_record, value):
        if not attribute_record or attribute_record.data_type != "boolean":
            return None
        return self.search(
            [("attribute_id", "=", attribute_record.id), ("active", "=", True)],
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
