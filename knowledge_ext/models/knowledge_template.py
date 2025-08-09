from odoo import models, fields, api


class KnowledgeTemplate(models.Model):
    _name = 'knowledge.template'
    _description = 'Knowledge Template'

    name = fields.Char(string="Name", required=True)
    body = fields.Html(string="Body")
    icon = fields.Char(string='Emoji')
    cover_image_id = fields.Many2one("knowledge.cover", string='Article cover')
    cover_image_url = fields.Char(related="cover_image_id.attachment_url", string="Cover url")
