from odoo import fields, models, api, _


class ProjectChecklist(models.Model):
    _name = 'project.checklist'

    name = fields.Char(string='Name', help='Project Progress Stages')
    project_id = fields.Many2one(comodel_name='project.project')
