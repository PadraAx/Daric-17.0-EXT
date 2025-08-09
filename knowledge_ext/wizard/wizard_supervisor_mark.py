from odoo import api , fields , models, _


class WizardSupervisorMark(models.TransientModel):
    _name = 'wizard.supervisor.mark'
    _description = 'Wizard Supervisor Mark'


    @api.depends('user_id')
    def _expert_group(self):
        for record in self:
            record.expert_group = False
            if self.env.user.has_group('knowledge_ext.group_knowledge_expert'):
                record.expert_group = True
                
    def _user_id_default(self):
        if self.env.user.has_group('knowledge_ext.group_knowledge_expert'):
            return self.env.user.id
        else:
            return False

            
    # ---------------------------------------------------
    #  Fields
    # ---------------------------------------------------
    
    user_id = fields.Many2one('res.users', string="Expert User", default=_user_id_default)
    message = fields.Char(string="Message", store=False, readonly=True)
    #access field
    expert_group = fields.Boolean(compute='_expert_group', string='Check Expert Access Group')
    request_id = fields.Many2one('knowledge.request')
    expert_ids = fields.Many2many(related='request_id.expert_ids')
        
        
    @api.depends_context('active_id')
    @api.onchange('user_id')
    def onchange_message(self):
        self.message = ''
        if self.user_id and self._context.get('active_id'):
            obj = self.sudo().env['knowledge.request'].browse(self._context['active_id'])
            if obj and obj.evaluation_ids.filtered(lambda r: r.score==0 and r.expert_id.id==self.user_id.id):
                self.message = 'You are passing one or more item score by zero, it will affect on the average score. do you still want to continue?'
            else:
                self.message = 'You are updating {} scores.'.format(self.user_id.name)
    
    def update_expert_score(self):
        if self.user_id and self._context.get('active_id'):
            request_obj = self.sudo().env['knowledge.request'].browse(self._context['active_id'])
            request_obj.evaluation_ids.filtered(lambda r: r.expert_id.id==self.user_id.id).write({'confirm': True})
            remain_confirm = request_obj.evaluation_ids.filtered(lambda r: r.confirm==False) 
            if not remain_confirm :
                request_obj.to_final()
                message =  _("Status changed into final review")
            else : 
                message =  _("Your score has been submit")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                        'type': 'success',
                        'title': _("Successfully!"),
                        'message': message,
                        'next': {'type': 'ir.actions.act_window_close'},
                }
            }       
        