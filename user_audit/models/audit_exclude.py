
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AuditExclude(models.Model):
    _name = 'audit.exclude'
    _description = 'Audit exclude'

