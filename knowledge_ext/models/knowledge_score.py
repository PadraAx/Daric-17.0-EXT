# -*- coding: utf-8 -*-
from random import randint
from operator import itemgetter
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class KnowledgeScore(models.Model):
    _name = 'knowledge.score'
    _description = 'Knowledge Score'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"


    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string='Score Details', tracking=True)
    factor = fields.Integer(string="Factor",default=1)


    @api.constrains('factor')
    def check_score(self):
        for record in self:
            if record.factor <= 0:
                raise UserError(_("Factor should bigger than 0"))