# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BldgFloorType(models.Model):
    _name = "bldg.floor.type"
    _description = "Floor Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    name = fields.Char(
        string=_("Type"),
        required=True,
        translate=True,
    )
    code = fields.Char(
        string=_("Code"),
        size=2,
        required=True,
    )
    sequence = fields.Integer(
        string=_("Sequence"),
        default=10,
    )
    active = fields.Boolean(
        string=_("Active"),
        default=True,
    )
    color = fields.Integer(
        string=_("Color"),
        help=_("Color for visual distinction in kanban and calendar views."),
    )
    description = fields.Text(
        string=_("Description"),
        translate=True,
    )
    floor_ids = fields.One2many(
        comodel_name="bldg.floor",
        inverse_name="floor_type_id",
        string="Floors with this Type",
    )
    # -------------------------------------------------------------------------
    # SQL Constraints
    # -------------------------------------------------------------------------
    _sql_constraints = [
        ("code_unique", "unique(code)", _("Floor-type code must be unique.")),
    ]

    # -------------------------------------------------------------------------
    # Create / Write
    # -------------------------------------------------------------------------
    @api.model
    def create(self, vals):
        if vals.get("code"):
            vals["code"] = vals["code"].upper()[:2]
        return super().create(vals)

    def write(self, vals):
        if vals.get("code"):
            vals["code"] = vals["code"].upper()[:2]
        return super().write(vals)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------
    @api.constrains("code")
    def _check_code_format(self):
        for rec in self:
            if not rec.code.isalnum():
                raise ValidationError(_("Code must be alphanumeric."))
