# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class BldgAttrStringScoringRule(models.Model):
    _name = "bldg.attr.string.scoring.rule"
    _description = _("Scoring Rules for String Attributes")
    _order = "attribute_id, sequence"
    _rec_name = "display_name"

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
        domain=[("data_type", "=", "string")],
    )
    sequence = fields.Integer(default=10)

    token_string = fields.Char(
        string="Tokens (comma-separated)",
        required=True,
        help="Case-insensitive, leading/trailing whitespace will be stripped.",
    )
    points = fields.Float(string=_("Points"), required=True)

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ------------------------------------------------------------------
    # COMPUTED
    # ------------------------------------------------------------------
    @api.depends("attribute_id", "token_string")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.attribute_id.name or _('(No attribute)')}: "
                f"{rec.token_string}"
            )

    # ------------------------------------------------------------------
    # CONSTRAINTS
    # ------------------------------------------------------------------
    @api.constrains("token_string")
    def _check_tokens(self):
        for rec in self:
            if not rec.token_string or not re.sub(r"\s+", "", rec.token_string):
                raise ValidationError(_("At least one token must be supplied."))

    # ------------------------------------------------------------------
    # BUSINESS API
    # ------------------------------------------------------------------
    @api.model
    def match_rule(self, attribute_record, value):
        """
        Return the first rule whose tokens are all found (substring match)
        in the supplied string value.
        """
        if not isinstance(value, str):
            return None
        if not attribute_record or attribute_record.data_type != "string":
            return None

        value_lc = value.strip().lower()
        for rule in self.search([("attribute_id", "=", attribute_record.id)]):
            tokens = [
                t.strip().lower() for t in rule.token_string.split(",") if t.strip()
            ]
            if tokens and all(t in value_lc for t in tokens):
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
