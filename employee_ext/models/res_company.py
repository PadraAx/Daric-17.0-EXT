# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'


    company_type = fields.Selection([('DMCC', 'DMCC'),
                                    ('LLC', 'LLC'),
                                    ('LTD', 'LTD'), ], string="Company Type", tracking=True)
    main_res_and_activities = fields.Text(string="Main Responsibility And Activities", tracking=True)
    register_location = fields.Many2one('res.country', 'Registered Location', tracking=True)
    legal_name = fields.Char('Legal Name', tracking=True)
    background_data = fields.Binary(string='Background', tracking=True)
    background_filename = fields.Char('Background File Name', tracking=True)
    icon_data = fields.Binary(string='Icon', tracking=True)
    icon_filename = fields.Char('Icon File Name', tracking=True)
    line_data = fields.Binary(string='line', tracking=True)
    line_filename = fields.Char('line File Name', tracking=True)
    stamp_data = fields.Binary('Stamp', tracking=True)
    stamp_filename = fields.Char('Stamp File Name', tracking=True)
    color_rgb = fields.Char('Color RGB')
    
    
    @api.model_create_multi
    def create(self, vals_list):
        companies = super(ResCompany, self).create(vals_list)
        users = self.env['res.users'].sudo().search([('all_companies', '=', True)]).ids
        for each in users:
            self.env['res.users'].browse(each).sudo().write({'company_ids': [(4, item) for item in companies.ids]})
        return companies
