from odoo import fields, models, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    checklist_ids = fields.One2many(comodel_name='project.checklist', string='Check list', inverse_name='project_id')

    progress = fields.Float("Progress", store=True, group_operator="avg",
                            help="Display progress of current task.")

    @api.onchange('checklist_ids')
    def _onchange_progress_checklist(self):
        for rec in self:
            line_ids = self.env['project.checklist'].search([]).ids
            lines = len(rec.mapped('checklist_ids'))
            if line_ids:
                rec.progress = round((lines / len(line_ids)) * 100)
            else:
                rec.progress = 0
