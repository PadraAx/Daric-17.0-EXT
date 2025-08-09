# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import models, fields, api
from odoo.tools import SQL


class Users(models.Model):
    _inherit = 'res.users'

    def get_erm_assignment_record(self):
        mapped_assignments = self.env['erm.risk.category'].search([('user_id', '=', self.env.uid)])
        allowed_category_ids = mapped_assignments.mapped('id')
        return [('category_id', 'in', allowed_category_ids)]
    
    def get_erm_risk_template_analyst_record(self):
        mapped_assignments = self.env['erm.risk.assignment'].search([('user_id', '=', self.env.uid),('active', '=', True)])
        allowed_category_ids = mapped_assignments.mapped('category_id').ids
        allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
        allowed_affected_area_ids = mapped_assignments.mapped('affected_area_ids').ids
        return [('category_id', 'in', allowed_category_ids),('risk_source_id', 'in', allowed_source_ids),('affected_area_id', 'in', allowed_affected_area_ids)]
    
    def get_erm_risk_analyst_record(self):
        mapped_assignments = self.env['erm.risk.assignment'].search([('user_id', '=', self.env.uid),('active', '=', True)])
        allowed_category_ids = mapped_assignments.mapped('category_id').ids
        allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
        allowed_affected_area_ids = mapped_assignments.mapped('affected_area_ids').ids
        return [('parent_id.category_id', 'in', allowed_category_ids),('parent_id.risk_source_id', 'in', allowed_source_ids),('parent_id.affected_area_id', 'in', allowed_affected_area_ids)]
    
    def get_erm_risk_template_owner_record(self):
        mapped_assignments = self.env['erm.risk.assignment'].search([('user_id', '=', self.env.uid),('active', '=', True)])
        allowed_category_ids = mapped_assignments.mapped('category_id').ids
        allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
        return [('category_id', 'in', allowed_category_ids),('risk_source_id', 'in', allowed_source_ids)]
    
    def get_erm_risk_owner_record(self):
        mapped_assignments = self.env['erm.risk.assignment'].search([('user_id', '=', self.env.uid),('active', '=', True)])
        allowed_category_ids = mapped_assignments.mapped('category_id').ids
        allowed_source_ids = mapped_assignments.mapped('risk_source_id').ids
        return [('parent_id.category_id', 'in', allowed_category_ids),('parent_id.risk_source_id', 'in', allowed_source_ids)]

    def get_erm_risk_template_manager_record(self):
        mapped_assignments = self.env['erm.risk.category'].search([('user_id', '=', self.env.uid)])
        allowed_category_ids = mapped_assignments.mapped('id')
        return [('category_id', 'in', allowed_category_ids)]
    
    def get_erm_risk_manager_record(self):
        mapped_assignments = self.env['erm.risk.category'].search([('user_id', '=', self.env.uid)])
        allowed_category_ids = mapped_assignments.mapped('id')
        return [('parent_id.category_id', 'in', allowed_category_ids)]