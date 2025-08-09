# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrDepartmentLayer(models.Model):
    _name = 'hr.department.layer'
    _description = 'Department Layer'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    
    name = fields.Char('Name', required=True, tracking=True)