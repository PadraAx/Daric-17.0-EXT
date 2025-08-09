from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    partner_group_id = fields.Many2one("res.partner.group", string="Partner group", copy=False)
    type_res = fields.Selection(
            selection=[('customer','Customer'),
            ('vendor','Vendor')], string='Partner type', compute="_partner_group")

    @api.depends('customer_rank','supplier_rank')
    def _partner_group(self):
        """record de type of groupe partner"""
        for res in self:
            if res.customer_rank >0:
                res.type_res = 'customer'
            elif res.supplier_rank >0:
                res.type_res = 'vendor'