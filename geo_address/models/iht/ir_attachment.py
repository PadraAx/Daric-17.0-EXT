# Inherit ir.attachment
from odoo import models, fields


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    blueprint_attachment = fields.Boolean(string="Is Blueprint?")
