# -*- coding: utf-8 -*-
from random import randint
from operator import itemgetter
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class knowledge_ambassador_item(models.Model):
    _name = 'knowledge.ambassador.item'
    _description = 'Knowledge Ambassador Item'


    #Fields
    name = fields.Char(string="Item", required=True, tracking=True)
    description = fields.Text(string='Ambassador Item Detail', tracking=True)       