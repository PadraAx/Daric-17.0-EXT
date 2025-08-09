from odoo import api , fields , models

class WizardTemplate(models.TransientModel):
    _name = 'wizard.template'
    _description = 'Wizard Template'

    template_id = fields.Many2one("knowledge.template", string='Template')
    is_private = fields.Boolean(string='is_private')
    article_id = fields.Many2one('knowledge.article', string='Article')



    def _open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Template Wizard',
            'res_model': 'wizard.template',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }

    def create_article(self):
        article_item = self.env['knowledge.article'].article_template_create({
            'name':self.template_id.name,
            'cover_image_id':self.template_id.cover_image_id.id,
            'icon':self.template_id.icon,
            'body':self.template_id.body,
            'parent_id':self.article_id.id if self.article_id else False,
            'is_article_item': False ,
        },self.article_id, self.is_private)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'knowledge.article',
            'res_id': article_item.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
        