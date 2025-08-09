# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Job(models.Model):
    _inherit = 'hr.job'
    _order = 'sequence, name'
    _sql_constraints = []

    @api.constrains('no_of_recruitment')
    def _check_no_of_recruitment_positive(self):
        for record in self:
            if record.no_of_recruitment < 0:
                raise ValidationError("The expected number of new employees must be positive.")

    @api.constrains('employee_id')
    def _check_unique_employee_id(self):
        for record in self:
            if record.employee_id:
                existing_employee = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_employee:
                    raise ValidationError("This employee has been assigned before.")

    # check this if we do not need it remove it
    position_status = fields.Selection([('tbr', 'Planned - TBR'),
                                        ('unplanned ', 'Unplanned but Available in Org Chart'),
                                        ('existing ', 'Planned - Existing'), ], string="Position Status", tracking=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    required=True, check_company=False, tracking=True)
    parent_id = fields.Many2one('hr.job', 'Manager', tracking=True)
    child_ids = fields.One2many('hr.job', 'parent_id', string='Direct subordinates', tracking=True)
    department_color = fields.Integer("Department Color", related="department_id.color",
                                      check_company=False, tracking=True)
    tier_id = fields.Many2one('hr.job.tier', "Tier", tracking=True)
    level_id = fields.Many2one('hr.job.level', 'Level', tracking=True)
    ref = fields.Integer(string='ref')
    sequence = fields.Integer('sequence', default=1, tracking=True)
    country_id = fields.Many2one('res.country', string='Country', tracking=True)
    no_of_recruitment = fields.Integer(string='Target', copy=False, tracking=True,
                                       help='Number of new employees you expect to recruit.', default=1)
    # employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string='Employee')
    employee_id = fields.Many2one('hr.employee', string='Employee', store=True,
                                  readonly=True, copy=False, tracking=True)
    employee_id_image = fields.Binary(related='employee_id.image_128')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # remove the hr_job_name_company_uniq index to have duplicate name

    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.name} ({record.country_id.name})'


class HrJobLevel(models.Model):
    _name = "hr.job.level"
    _description = "Job Level"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True,)


class HrJobTier(models.Model):
    _name = "hr.job.tier"
    _description = "Job Tier"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Name", required=True, tracking=True,)
    code = fields.Char('Code', required=True, tracking=True,)
    skip_travel_manager = fields.Boolean(string='Skip Travel Manager', default=False)
