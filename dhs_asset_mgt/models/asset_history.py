from odoo import models, fields


class AssetHistory(models.Model):
    _name = 'asset.history'
    _description = "Asset History Model"
    _order = "date "

    asset_id = fields.Many2one('asset.component', string='Asset')
    user_id = fields.Many2one('res.partner', string='User')
    action = fields.Selection(
        selection=[
            ("running", "Running"),
            ("returned", "Returned"),
            ("reassigment", "Reassigment"),
            ("retired", "Retired"),
        ],
        string="Action")
    date = fields.Datetime(string="Date")
    description = fields.Char(string="Description")
    assign_id = fields.Many2one('res.partner', string='Assign')
    inventory_id = fields.Many2one('stock.picking', string='Link')

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.action}-{record.date.strftime('%Y-%m-%d')}"

    def action_to_inventory(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.inventory_id.name,
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.inventory_id.id,
        }
