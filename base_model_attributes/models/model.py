# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = 'ir.model'

    def button_display_attributes(self):
        self.ensure_one()
        obj = self.env[self.model]
        ignored = ['_cache']
        attributes = [a for a in dir(obj) if a not in ignored and not callable(getattr(obj, a))]
        attributes = [a for a in attributes if a not in self.field_id.mapped('name')]
        attributes = [a for a in attributes if a not in ('<lambda>', )]
        return self.popup(title="Attributes", message="\n".join(sorted(attributes)))

    def button_display_methods(self):
        self.ensure_one()
        obj = self.env[self.model]
        ignored = ['_cache']
        attributes = [a for a in dir(obj) if a not in ignored and callable(getattr(obj, a))]
        return self.popup(title="Methods", message="\n".join(sorted(attributes)))

