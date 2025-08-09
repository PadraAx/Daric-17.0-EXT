# -*- coding: utf-8 -*-
from random import randint
from operator import itemgetter
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class knowledge_request_ambassador_item(models.Model):
    _name = 'knowledge.request.ambassador.item'
    _description = 'Knowledge Request Ambassador Item'


    # Fields
    done = fields.Boolean(string='Done', tracking=True, default=False)
    request_id = fields.Many2one("knowledge.request", string="Requester", required=True, tracking=True, readonly=True, ondelete='cascade')
    ambassador_item_id = fields.Many2one("knowledge.ambassador.item", string="Ambassador Item", required=True, tracking=True, readonly=True, ondelete='cascade')
    ambassador_item_desc = fields.Text(related="ambassador_item_id.description")


    def open_details(self):
        return {
        'name': _('Ambassador Checklist item'),
        'target': 'new',
        'type': 'ir.actions.act_window',
        'view_mode': 'form',
        'res_id': self.id,
        'res_model': 'knowledge.request.ambassador.item',
        'view_id': self.env.ref('knowledge_ext.view_knowledge_request_ambassador_item_readonly_form').id
    }