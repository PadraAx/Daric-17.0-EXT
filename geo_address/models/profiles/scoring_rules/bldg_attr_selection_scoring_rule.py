# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgAttrSelectionScoringRule(models.Model):
    _name = "bldg.attr.selection.scoring.rule"
    _description = _("Scoring Rules for Selection Attributes")
    _order = "attribute_id, selection_key"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "selection_unique",
            "UNIQUE(attribute_id, selection_key)",
            _("Selection rules must be unique per attribute."),
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
        domain=[("data_type", "=", "selection")],
    )
    selection_key = fields.Char(string=_("Selection Key"), required=True)
    selection_value = fields.Char(string=_("Human-readable label"))
    points = fields.Float(string=_("Points"), required=True)

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ==============================================================================
    # METHODS
    # ==============================================================================
    @api.depends("attribute_id", "selection_key", "selection_value")
    def _compute_display_name(self):
        for rec in self:
            attr = rec.attribute_id.name or _("(No attribute)")
            label = rec.selection_value or rec.selection_key or _("(No key)")
            rec.display_name = f"{attr}: {label}"

    @api.model
    def match_rule(self, attribute_record, value):
        if not attribute_record or attribute_record.data_type != "selection":
            return None
        key = str(value or "no_selection")
        return self.search(
            [
                ("attribute_id", "=", attribute_record.id),
                ("selection_key", "=", key),
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
