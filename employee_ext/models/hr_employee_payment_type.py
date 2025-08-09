# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeePaymentType(models.Model):
    _name = 'hr.employee.payment.type'
    _description = 'Employee Payment Type'
    
    
    
    name = fields.Char('name')