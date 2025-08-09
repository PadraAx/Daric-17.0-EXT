from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class BPMProcess(models.Model):
    _name = "bpm.process"
    _description = "Process"

    code = fields.Char(string='Code', required=False, readonly = True, index=True, copy=True)
    # businessdomain_category_id = fields.Many2one('business.domain.categories', required=True, string="Business Domain Category", domain="[('active', '=', True)]")
    business_domain_id = fields.Many2one('requirement.business.domains', required=True, string="Business Domain",
                                                  domain="[('active', '=', True)]")
    businessdomain_category_id =  fields.Many2one(string='Business Domain Category',
                                      related="business_domain_id.businessdomain_category_id", related_sudo=True, store=True,readonly = True)
    active = fields.Boolean(string="Active", default=True, copy=False)
    name = fields.Text(string='Title', required=True)
    process_type = fields.Selection(selection=[ ('1','Passive'),
                                                ('2','Active'),
                                              ],string='Process',default='1') 
    workflow_id = fields.Many2one('workflow.base',string="workflow")
    document_ids = fields.Many2many('documents.document', string='Documents',tracking=True)

    


    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search_count([('id', '!=', record.id), ('name', '=', record.name),('business_domain_id', '=', record.business_domain_id.id)]) > 0:
                raise ValidationError("Name must be unique, per business domain!")

  
    @api.onchange('workflow_id')
    def onchange_workflow_id(self):
            if self.workflow_id:
                self.process_type="2"
            else:
                self.process_type="1"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            business_domain_id = vals.get('business_domain_id') 
            if business_domain_id:
                business_domain = self.env['requirement.business.domains'].browse(business_domain_id)
                if 'code' not in vals:
                    seq_name = f'bpm_process.seq.{business_domain.name}.{business_domain.id}'
                    sequence = self.env['ir.sequence'].search([('code', '=', seq_name)], limit=1)
                    if not sequence:
                            sequence = self.env['ir.sequence'].create({
                                'name': seq_name,
                                'code': seq_name,
                                'padding': '3',  # Adjust padding as needed
                                'implementation': 'standard', 
                                'number_increment': '1', 
                                'number_next': '0', 
                            })
                    vals['code'] = f'{business_domain.code}{sequence.next_by_code(seq_name)}'
        return super(BPMProcess, self).create(vals_list)