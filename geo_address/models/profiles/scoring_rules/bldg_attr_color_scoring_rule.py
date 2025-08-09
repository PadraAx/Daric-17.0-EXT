# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class BldgAttrColorScoringRule(models.Model):
    _name = "bldg.attr.color.scoring.rule"
    _description = _("Scoring Rules for Color Attributes")
    _order = "attribute_id, sequence"
    _rec_name = "display_name"

    _sql_constraints = [
        (
            "unique_color_range",
            "UNIQUE(attribute_id, color_from, color_to)",
            _("This color range already exists for the attribute."),
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
        domain=[("data_type", "=", "color")],
    )
    sequence = fields.Integer(default=10)

    color_from = fields.Char(
        string="Bottom Color (HEX)",
        size=7,
        help="HEX format like #00FF00 for the bottom of the spectrum.",
    )
    color_to = fields.Char(
        string="Top Color (HEX)",
        size=7,
        help="HEX format like #FF0000 for the top of the spectrum.",
    )
    points = fields.Float(string=_("Points"), required=True)

    active = fields.Boolean(default=True)
    description = fields.Text(string=_("Internal note"))

    # ------------------------------------------------------------------
    # COMPUTED
    # ------------------------------------------------------------------
    @api.depends("attribute_id", "color_from", "color_to")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.attribute_id.name or _('(No attribute)')}: "
                f"{rec.color_from} – {rec.color_to}"
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

    # ------------------------------------------------------------------
    # CONSTRAINTS
    # ------------------------------------------------------------------
    @api.constrains("color_from", "color_to")
    def _check_hex_format(self):
        regex = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for rec in self:
            if rec.color_from and not regex.match(rec.color_from):
                raise ValidationError(_("Bottom color must be a valid 6-digit HEX."))
            if rec.color_to and not regex.match(rec.color_to):
                raise ValidationError(_("Top color must be a valid 6-digit HEX."))

    # ------------------------------------------------------------------
    # BUSINESS API
    # ------------------------------------------------------------------
    @api.model
    def match_rule(self, attribute_record, value_hex):
        """
        Return the rule whose color range contains the given HEX color.
        `value_hex` must be '#RRGGBB' string (case-insensitive).
        """
        if not attribute_record or attribute_record.data_type != "color":
            return None
        if not isinstance(value_hex, str):
            return None

        value_hex = value_hex.upper().strip()
        regex = re.compile(r"^#[0-9A-Fa-f]{6}$")
        if not regex.match(value_hex):
            return None

        # Simple linear comparison of HEX values
        return self.search(
            [
                ("attribute_id", "=", attribute_record.id),
                ("color_from", "<=", value_hex),
                ("color_to", ">=", value_hex),
                ("active", "=", True),
            ],
            limit=1,
        )
