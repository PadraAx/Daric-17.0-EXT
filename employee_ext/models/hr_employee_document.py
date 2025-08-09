# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'Employee Document'


    document_no = fields.Char(string="Document No")
    document_type_id = fields.Many2one('hr.document.type', string="Document Type")
    expiry_date = fields.Date(string="Expiry Date")
    data = fields.Binary(string='File', help="Export file related to this Letter", required=True)
    filename = fields.Char('File Name')
    employee_id = fields.Many2one('hr.employee', string="employee")
