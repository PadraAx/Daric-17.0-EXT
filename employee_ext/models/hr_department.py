# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Department(models.Model):
    _inherit = 'hr.department'
    _order = 'sequence, name'

    active = fields.Boolean('Active', default=True, tracking=True)
    name = fields.Char('Department Name', required=True, translate=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.company, tracking=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True, check_company=False)
    parent_id = fields.Many2one('hr.department', string='Parent Department', index=True,
                                check_company=True, domain="[('id','!=', id)]", tracking=True)
    color = fields.Integer('Color Index', tracking=True)
    # new fields
    hrbp_id = fields.Many2one('hr.employee', string='HRBP', tracking=True)
    hrbp_associate_ids = fields.Many2many('hr.employee', 'employee_hrbpids',
                                          'employee_id', 'hrbp_ids', string='HRBP Associate', tracking=True)
    layer_id = fields.Many2one('hr.department.layer', string='Layer', tracking=True)
    sequence = fields.Integer('sequence', default=1, tracking=True)
    local_name = fields.Char('Local Name', tracking=True)
