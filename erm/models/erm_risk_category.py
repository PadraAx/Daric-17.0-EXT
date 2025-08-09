from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskCategory(models.Model):
    _name = "erm.risk.category"
    _description = "Risk Categories"

    name = fields.Char(string='Title',required=True, )
    description = fields.Text(string='Description')
    # category_type_id = fields.Many2one('erm.risk.category.type', 'Type')
    code =  fields.Text(string='Code')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                string="Company",
                                default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                 related='company_id.currency_id',
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)

    risk_tolerance = fields.Monetary(string="Risk tolerance", currency_field='currency_id', group_operator='sum',
                                      help="Risk tolerance refers to the amount of loss an investor is prepared to handle while making an investment decision.")
    tag_ids = fields.Many2many('erm.risk.tag', string='Tags',tracking=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Risk Manager',domain=lambda self: [("groups_id", "=", self.env.ref( "erm.erm_group_manager" ).id)])
    

    @api.onchange('user_id')
    def _onchange_user_id(self):
        group = self.env.ref('erm.erm_group_manager')
        self.currency_id = self.user_id.company_id.currency_id.id
        return {'domain': {'user_id': [('groups_id', 'in', [group.id])]}}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
                if 'code' not in vals:
                    seq_name =  f'erm_risk_category.seq'
                    sequence = self.env['ir.sequence'].search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '2',  # Adjust padding as needed
                                'implementation': 'standard', 
                                'number_increment': '1', 
                                'number_next': '0', 
                            })

                    vals['code'] =f'{sequence.next_by_code(seq_name)}'
                # if 'currency_id' not in vals:
                #      vals['currency_id'] = self.env.user.company_id.currency_id.id
                     
        return  super(ERMRiskCategory, self).create(vals_list)