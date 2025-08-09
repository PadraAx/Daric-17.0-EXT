# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import operator
import math


class BldgCalcParam(models.Model):
    _name = "bldg.calc.param"
    _description = "Calculation Parameter (Operand)"
    _order = "sequence, id"

    group_id = fields.Many2one(
        "bldg.calc.group", required=True, string="Calculation Group", ondelete="cascade"
    )

    calc_param_id = fields.Many2one(
        "bldg.profile.attribute.line",
        required=True,
        string="Attribute Line",
        domain="[('attribute_id.data_type', 'in', ('integer', 'float'))]",
        help="Profile attribute line supplying a numeric value for this operand.",
    )

    value_integer = fields.Integer(related="calc_param_id.value_integer", store=True)
    value_float = fields.Float(related="calc_param_id.value_float", store=True)

    sequence = fields.Integer(
        string="Order", default=10, help="Order among parameters of the same group."
    )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------
    @api.constrains("calc_param_id", "group_id")
    def _check_not_target_param(self):
        for rec in self:
            if rec.calc_param_id.attribute_id == rec.group_id.target_param_id:
                raise ValidationError(
                    f"Parameter '{rec.calc_param_id.name}' cannot reference "
                    f"the target attribute ('{rec.group_id.target_param_id.name}') "
                    f"of its group."
                )
