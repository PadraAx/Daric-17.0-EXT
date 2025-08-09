
from odoo import fields, models


class HrEmployeeTraining(models.Model):
    _name = 'hr.employee.training'
    _description = 'Hr Employee Training'
    
    
    training_program = fields.Char('Program')
    training_date = fields.Date('Date')
    tarining_duration = fields.Char('Duration')
    training_provider = fields.Char('Provider')
    training_location = fields.Char('Location')
    completion_status = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Completion Status')
    certificate_provided = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Certificate Provided')
    filename = fields.Char('File Name')
    attachment = fields.Binary('Attachment', attachment=True)
    employee_id = fields.Many2one('hr.employee', string="employee")