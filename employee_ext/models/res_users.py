# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from odoo import api, fields, models, _

from odoo.addons.hr.models.res_users import HR_WRITABLE_FIELDS


# HR_WRITABLE_FIELDS.extend([
#     'first_name',
#     'last_name',
#     'nationality',
#     'other_nationality',
#     'religion',
#     'dependent_number',
#     'father_name',
#     'mother_name',
#     'home_country_address_id',
#     'second_phone',
#     'emergency_relation',
#     'emergency_email',
#     'emergency_address',
#     'bank_name',
#     'bank_account',
#     'swift_code',
#     'branch_location',
#     'iban_no',
#     'ifsc_code',
#     'image_1920',
#     'education_ids',
# ])


class User(models.Model):
    _inherit = 'res.users'


    first_name = fields.Char(related='employee_id.first_name', readonly=True, tracking=True, )
    last_name = fields.Char(related='employee_id.last_name', readonly=True, tracking=True, )
    nationality = fields.Char(related='employee_id.nationality', readonly=True, tracking=True, )
    other_nationality = fields.Char(related='employee_id.other_nationality', readonly=True, tracking=True, )
    religion = fields.Many2one(related='employee_id.religion', readonly=True, tracking=True, )
    marital = fields.Selection(related='employee_id.marital', readonly=True, related_sudo=False)
    children = fields.Integer(related='employee_id.children', readonly=True, related_sudo=False)
    dependent_number = fields.Integer(related='employee_id.dependent_number', readonly=True)
    father_name = fields.Char(related='employee_id.father_name', readonly=True, tracking=True, )
    mother_name = fields.Char(related='employee_id.mother_name', readonly=True, tracking=True, )
    home_country_address_id = fields.Char(
        related='employee_id.home_country_address_id', readonly=True, tracking=True, )
    second_phone = fields.Char(related='employee_id.second_phone', readonly=True, tracking=True, related_sudo=False)
    emergency_relation = fields.Many2one(related='employee_id.emergency_relation', readonly=True, tracking=True, )
    emergency_email = fields.Char(related='employee_id.emergency_email', readonly=True, tracking=True, )
    emergency_address = fields.Char(related='employee_id.emergency_address', readonly=True, tracking=True, )
    bank_name = fields.Char(related='employee_id.bank_name', readonly=True, tracking=True, )
    bank_account = fields.Char(related='employee_id.bank_account', readonly=True, tracking=True, )
    swift_code = fields.Char(related='employee_id.swift_code', readonly=True, tracking=True, )
    branch_location = fields.Char(related='employee_id.branch_location', readonly=True, tracking=True, )
    iban_no = fields.Char(related='employee_id.iban_no', readonly=True, tracking=True, )
    ifsc_code = fields.Char(related='employee_id.ifsc_code', readonly=True, tracking=True, )
    education_ids = fields.One2many(related='employee_id.education_ids', readonly=True, tracking=True, )
    all_companies = fields.Boolean('Access To All Companies', tracking=True)


    @api.depends('employee_ids')
    @api.depends_context('company')
    def _compute_company_employee(self):
        employee_data = self.env['hr.employee'].search([('user_id', 'in', self.ids)])
        employee_per_user = defaultdict(dict)
        for employee in employee_data:
            employee_per_user[employee.user_id.id][employee.company_id.id] = employee.id
        for user in self:
            user_data = employee_per_user[user.id]
            user.employee_id = user_data.get(self.env.company.id) or (list(user_data.values()) or [False])[0]

    @api.constrains('image_1920', 'image_128')
    def update_images(self):
        for user in self:
            user.employee_id.image_1920 = self.image_1920
            user.employee_id.image_128 = self.image_128

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('all_companies'):
                vals['company_ids'] = self.env['res.company'].sudo().search([]).ids
        return super(User, self).create(vals_list)

    def write(self, values):
        if values.get('all_companies') == True:
            values['company_ids'] = self.env['res.company'].sudo().search([]).ids
        return super(User, self).write(values)

    # @property
    # def SELF_WRITEABLE_FIELDS(self):
    #     res = super().SELF_WRITEABLE_FIELDS
    #     return [item for item in res if item not in HR_WRITABLE_FIELDS]
