# -*- coding: utf-8 -*-
from random import randint
from operator import itemgetter
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class KnowledgeRequestScore(models.Model):
    _name = 'knowledge.request.score'
    _description = 'Request Score'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "expert_id asc, score_id asc"


    score = fields.Integer(string="Score", tracking=True, default=0)
    request_id = fields.Many2one("knowledge.request", string="Requester", required=True, tracking=True, readonly=True, ondelete='cascade')
    score_id = fields.Many2one("knowledge.score", string="item", required=True, tracking=True, readonly=True)
    expert_id = fields.Many2one("res.users", string="Expert User", required=True, tracking=True, readonly=True)
    score_desc = fields.Text(related="score_id.description")
    factor = fields.Integer(related="score_id.factor")
    confirm = fields.Boolean(string='Confirm', tracking=True, default=False, readonly=True)


    @api.constrains('score')
    def check_score(self):
        for record in self:
            if not 0 <= record.score <= 10:
                raise UserError(_("Score should between 0 to 10"))

    def open_details(self):
        return {
        'name': _('Expert checklist score'),
        'target': 'new',
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'knowledge.request.score',
        'view_id': self.env.ref('knowledge_ext.view_knowledge_request_score_readonly_form').id
    }
        
class KnowledgeRequestScoreAvg(models.Model):
    _name = 'knowledge.request.score.avg'
    _description = 'Request Score Avarage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "score_id asc"


    score_avg = fields.Integer(string="Score Average", tracking=True, default=0,  readonly=True)
    request_id = fields.Many2one("knowledge.request", string="Requester", required=True, tracking=True, readonly=True, ondelete='cascade')
    score_id = fields.Many2one("knowledge.score", string="item", required=True, readonly=True)
    factor = fields.Integer(related="score_id.factor")
    score_desc = fields.Text(related="score_id.description")
