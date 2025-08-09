# -*- coding: utf-8 -*-

from odoo import fields, models


class HrTaminJob(models.Model):
    _name = "hr.tamin.job"
    _description = "Tamin Job"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, tracking=True,)
    code = fields.Char(string="Code", required=True, tracking=True,)

    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.name}-[{record.code}]'
