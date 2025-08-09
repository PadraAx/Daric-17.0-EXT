from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class FinancialImpact(models.Model):
    _name = 'financial.impact'
    _description = 'Financial Impact'

    name = fields.Char(string='Title',required=True)
    description = fields.Text(string='Description')
    direct_cost = fields.Monetary(string="Direct Costs", required=True, currency_field='currency_id',
                                   help="Estimate direct costs (e.g., repair costs, lost revenue).")
    indirect_cost = fields.Monetary(string="Indirect Costs", required=True, currency_field='currency_id',
                                     help="Estimate indirect costs (e.g., brand damage, regulatory fines).")

   