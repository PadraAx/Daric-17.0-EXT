# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrStationRent(models.Model):
    _name = "hr.station.rent"
    _description = "Station Rent"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    
    @api.depends('monthly_rent_lc', 'exchange_rate')
    def _calculate_rent_values(self):
        for record in self:
            if record.monthly_rent_lc:
                record.annual_rent_lc = record.monthly_rent_lc * 12
                if record.exchange_rate:
                    record.monthly_rent_usd = record.monthly_rent_lc / record.exchange_rate
                    record.annual_rent_usd = record.annual_rent_lc / record.exchange_rate


    from_date = fields.Datetime("From Date", tracking=True,)
    to_date = fields.Datetime("To Date", tracking=True,)
    station_id = fields.Many2one('hr.work.location', string="Station", tracking=True)
    exchange_rate = fields.Integer('Exchange Rate', tracking=True)
    monthly_rent_lc = fields.Integer('Monthly Rent LC', tracking=True)
    annual_rent_lc = fields.Integer('Annual rent LC', compute="_calculate_rent_values", default=0, store=True, tracking=True)
    monthly_rent_usd = fields.Integer('Monthly Rent USD', compute="_calculate_rent_values", default=0, store=True, tracking=True)
    annual_rent_usd = fields.Integer('Annual rent USD', compute="_calculate_rent_values", default=0, store=True, tracking=True)
    active_status = fields.Boolean('Active', tracking=True)
    
    
    @api.constrains('active_status')
    def single_active_record(self):
        for record in self:
            if record.active_status and self.search([('active_status', '=', True),
                                                     ('station_id', '=', record.station_id.id),
                                                     ('id', '!=', record.id)]):
                raise ValidationError("There is another active record.")