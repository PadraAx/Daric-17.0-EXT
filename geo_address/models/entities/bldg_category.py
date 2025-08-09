from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BldgCategory(models.Model):
    _name = "bldg.category"
    _description = "Building Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, code, name"

    name = fields.Char(
        string="Building Type",
        required=True,
        translate=True,
        trim=True,
    )

    code = fields.Char(
        string="Type Code",
        index=True,
        trim=True,
        required=True,
    )
    color = fields.Integer(
        string="Color",
        help="Color for visual distinction in kanban and calendar views",
    )
    description = fields.Text(
        string="Description",
        translate=True,
    )

    sequence = fields.Integer(
        default=10,
    )
    building_ids = fields.One2many(
        comodel_name="bldg.building",
        inverse_name="category_id",
        string="Buildings in this Category",
    )

    @api.constrains("code")
    def _check_code_format(self):
        for record in self:
            if record.code:
                if len(record.code) != 4:
                    raise ValidationError(_("Code must be exactly 4 characters long."))
                if not record.code.isalpha():
                    raise ValidationError(
                        _("Code must contain only alphabetical characters.")
                    )

    @api.model
    def create(self, vals):
        if "code" in vals and vals["code"]:
            vals["code"] = vals["code"].upper()[:4]
        return super(BldgCategory, self).create(vals)

    def write(self, vals):
        if "code" in vals and vals["code"]:
            vals["code"] = vals["code"].upper()[:4]
        return super(BldgCategory, self).write(vals)
