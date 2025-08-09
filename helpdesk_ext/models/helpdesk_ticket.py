import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    name = fields.Char(string='Subject')
    team_id = fields.Many2one('helpdesk.team', string="Team")
    user_id = fields.Many2one('res.users', string="Assigned User",  domain="[('id', 'in', domain_user_ids)]")
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_user_ids', store=False)
    user_has_admin_group = fields.Boolean(string="User has Admin Group", compute='_compute_user_has_admin_group', store=False)
    
    @api.model
    def default_get(self, fields):
        res = super(HelpdeskTicket, self).default_get(fields)
        res.update({'team_id': False, 'user_id': False})
        return res

    @api.onchange('team_id')
    def onchange_team_id(self):
      if self.team_id:
          self.user_id = False 
    
    @api.depends('team_id')
    def _compute_domain_user_ids(self):
        for ticket in self:
            if ticket.team_id:
                ticket.domain_user_ids = ticket.team_id.member_ids
            else:
                ticket.domain_user_ids = False    
                    
    @api.depends('user_id')
    def _compute_user_has_admin_group(self):
        for record in self:
            record.user_has_admin_group = self.env.user.has_group('helpdesk.group_helpdesk_manager')