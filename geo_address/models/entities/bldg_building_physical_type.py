# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class BldgBuildingPhysicalType(models.Model):
    _name = "bldg.building.physical.type"
    _description = "Building Physical Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    code = fields.Char(string="Code", required=True, tracking=True)
    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(
        string="Priority",
        help="Determines display order in dropdowns (lower numbers show first)",
        default=10,
    )
    color = fields.Integer(
        string="Color",
        help="Color for visual distinction in kanban and calendar views",
    )
    active = fields.Boolean(default=True)
    building_ids = fields.One2many(
        comodel_name="bldg.building",
        inverse_name="physical_type_id",
        string="Buildings in this Category",
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Code must be unique!"),
    ]

    @api.constrains("code")
    def _check_code_format(self):
        for record in self:
            if not re.match(r"^[A-Za-z]{2}$", record.code):
                raise ValidationError(
                    _("Code must be exactly 2 alphabetical characters")
                )

    @api.model
    def create(self, vals):
        if "code" in vals:
            vals["code"] = vals["code"].upper() if vals["code"] else False
        return super().create(vals)

    def write(self, vals):
        if "code" in vals:
            vals["code"] = vals["code"].upper() if vals["code"] else False
        return super().write(vals)
