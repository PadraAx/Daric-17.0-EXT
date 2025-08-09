# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrStationDeposit(models.Model):
    _name = "hr.station.deposit"
    _description = "Station Deposit"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    @api.depends('deposite_lc')
    def _calculate_deposit_usd(self):
        for record in self:
            if record.exchange_rate:
                record.deposite_usd = record.deposite_lc / record.exchange_rate
        

    from_date = fields.Datetime("From Date", tracking=True,)
    to_date = fields.Datetime("To Date", tracking=True,)
    exchange_rate = fields.Integer('Exchange Rate', tracking=True)
    station_id = fields.Many2one('hr.work.location', string="Station", tracking=True)
    deposite_lc = fields.Integer('Deposite LC', tracking=True)
    deposite_usd = fields.Integer('Deposite USD', compute="_calculate_deposit_usd", default=0, store=True, tracking=True)
    active_status = fields.Boolean('Active', tracking=True)
    
    
    @api.constrains('active_status')
    def single_active_record(self):
        for record in self:
            if record.active_status and self.search([('active_status', '=', True),
                                                     ('station_id', '=', record.station_id.id),
                                                     ('id', '!=', record.id)]):
                raise ValidationError("There is another active record.")