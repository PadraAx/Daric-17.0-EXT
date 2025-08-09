from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class ERMRiskCategoryType(models.Model):
    _name = "erm.risk.category.type"
    _description = "Risk Category Types"

    name = fields.Char(string='Title',required=True, readonly = False, store =True, index=False, copy=True,  tracking=False)
    description = fields.Text(string='Description')
    active = fields.Boolean(string="Active", default=True, copy=False)
    code =  fields.Text(string='Code')
    tag_ids = fields.Many2many('erm.risk.tag', string='Tags',tracking=True)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'code' not in vals:
                seq_name = 'erm_risk_category_type.seq'
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
                vals['code'] = sequence.next_by_code(seq_name)
        return  super(ERMRiskCategoryType, self).create(vals_list)
    
