from odoo import api, fields, models, _


class ERMRiskAffectedArea(models.Model):
    _name = "erm.risk.affected.area"
    _description = "Risk Affected Areas"

    name = fields.Char(string="Name", required=True)
    category_id = fields.Many2one(
        "erm.risk.category",
        "Category",
    )
