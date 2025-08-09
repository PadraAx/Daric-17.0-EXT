from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskSource(models.Model):
    _name = "erm.risk.source"
    _description = "Risk Source"

    name = fields.Char(string='Title',required=True, readonly = False, store =True)
    category_id = fields.Many2one('erm.risk.category', 'Category')
    description = fields.Text(string='Description')
    # category = fields.Selection(
    #     selection=[
    #         ("1", "Physical"),
    #         ("2", "Human"),
    #         ("3", "Organizational"),
    #         ("4", "Technological"),
    #         ("5", "Economic"),
    #         ("6", "Environmental"),
    #         ("7", "Legal/Regulatory"),
    #         ("8", "Social/Cultural"),
    #     ],
    #     string='Category', tracking=True)
