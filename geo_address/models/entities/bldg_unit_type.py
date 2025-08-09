# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BldgUnitType(models.Model):
    _name = "bldg.unit.type"
    _description = "Unit / Component Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "type_allowed_layer, code"

    name = fields.Char(string=_("Type Name"), required=True, translate=True)
    code = fields.Char(
        string=_("Code"),
        size=4,
        required=True,
        help=_("Exactly 4 alphabetical characters"),
    )
    type_allowed_layer = fields.Selection(
        selection=[
            ("1", _("Layer 1")),
            ("2", _("Layer 2")),
            ("3", _("Layer 3")),
            ("all", _("All Layers")),
        ],
        string=_("Allowed Layer"),
        required=True,
    )
    sequence = fields.Integer(string=_("Sequence"), default=10)
    active = fields.Boolean(string=_("Active"), default=True)
    color = fields.Integer(
        string="Color",
        help="Color for visual distinction in kanban and calendar views",
    )
    description = fields.Text(
        string="Description",
        translate=True,
    )
    unit_ids = fields.One2many(
        comodel_name="bldg.unit",
        inverse_name="unit_type_id",
        string="Units with this Type",
    )
    _sql_constraints = [
        ("code_unique", "unique(code)", _("Type code must be unique.")),
    ]

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if not rec.code or len(rec.code) != 4 or not rec.code.isalpha():
                raise ValidationError(
                    _("Code must be exactly 4 alphabetical characters.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code"):
                vals["code"] = vals["code"].upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("code"):
            vals["code"] = vals["code"].upper()
        return super().write(vals)
