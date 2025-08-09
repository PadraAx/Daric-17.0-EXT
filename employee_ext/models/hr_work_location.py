# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError


class WorkLocation(models.Model):
    _name = "hr.work.location"
    _inherit = ['hr.work.location', 'mail.thread.main.attachment',
                'mail.thread', 'mail.activity.mixin']


    @api.depends('deposit_lc', 'forex_impact_rate')
    def _compute_hc_deposit(self):
        for record in self:
            record.forex_deposit_lc = record.deposit_lc * record.forex_impact_rate * \
                12 if record.deposit_lc and record.forex_impact_rate else 0

    @api.depends('public_emp_ids', 'seats')
    def _compute_occupied_seats(self):
        for record in self:
            record.occupied_seats = len(record.public_emp_ids)
            record.vacant_seats = record.seats - record.occupied_seats
            record.occupied_percent = (record.occupied_seats / record.seats) if record.seats and record.occupied_seats else 0

    @api.depends('forex_impact_rate', 'forex_deposit_lc', 'fit_out_cost_lc', 'furniture_cost_lc', 'designer_fee_lc', 'pantry_admin_lc', 'it_cost_lc', 'commissions_extra_lc')
    def _compute_usd_values(self):
        for record in self:
            if record.initial_exchange_rate:
                record.forex_deposit_usd = record.forex_deposit_lc / record.initial_exchange_rate
                record.fit_out_cost_usd = record.fit_out_cost_lc / record.initial_exchange_rate
                record.furniture_cost_usd = record.furniture_cost_lc / record.initial_exchange_rate
                record.designer_fee_usd = record.designer_fee_lc / record.initial_exchange_rate
                record.pantry_admin_usd = record.pantry_admin_lc / record.initial_exchange_rate
                record.it_cost_usd = record.it_cost_lc / record.initial_exchange_rate
                record.commissions_extra_usd = record.commissions_extra_lc / \
                    record.initial_exchange_rate

    @api.depends('rent_lines.annual_rent_lc', 'forex_deposit_lc', 'fit_out_cost_lc', 'furniture_cost_lc', 'designer_fee_lc', 'pantry_admin_lc', 'it_cost_lc', 'commissions_extra_lc')
    def compute_total_cost_lc(self):
        for record in self:
            annual_rent_lc = record.rent_lines.filtered('active_status').annual_rent_lc if len(record.rent_lines.filtered('active_status')) == 1 else 0
            record.total_cost_lc = sum([annual_rent_lc, record.forex_deposit_lc, record.fit_out_cost_lc, record.furniture_cost_lc, record.designer_fee_lc,
                                       record.pantry_admin_lc, record.it_cost_lc, record.commissions_extra_lc])

    @api.depends('rent_lines.annual_rent_usd', 'forex_deposit_usd', 'fit_out_cost_usd', 'furniture_cost_usd', 'designer_fee_usd', 'pantry_admin_usd', 'it_cost_usd', 'commissions_extra_usd')
    def compute_total_cost_usd(self):
        for record in self:
            annual_rent_usd = record.rent_lines.filtered('active_status').annual_rent_usd if len(record.rent_lines.filtered('active_status')) == 1 else 0
            record.total_cost_usd = sum([annual_rent_usd, record.forex_deposit_usd, record.fit_out_cost_usd, record.furniture_cost_usd, record.designer_fee_usd,
                                        record.pantry_admin_usd, record.it_cost_usd, record.commissions_extra_usd])

    @api.depends('office_area_sqft')
    def _compute_office_area_sqm(self):
        for record in self:
            record.office_area = record.office_area_sqft * \
                0.092903 if record.office_area_sqft else 0

    @api.depends('office_area')
    def _compute_office_area_sqft(self):
        for record in self:
            record.office_area_sqft = record.office_area * \
                10.7639 if record.office_area else 0


    name = fields.Char(string="Stations Name", required=True)
    company_id = fields.Many2one('res.company', string="Entity", required=False, default=lambda self: self.env.company, tracking=True)
    address_id = fields.Many2one('res.partner', required=False, string="Work Address", check_company=True, domain=[('is_location', '=', True)])
    # new fields
    country_id = fields.Many2one(string="Location", related='address_id.country_id', store=True, )
    public_emp_ids = fields.One2many('hr.employee.public', 'work_location_id', string='Employees', domain=[('sit_taker', '=', 'yes'), ('active', '=', True)])
    business_unit = fields.Many2one('hr.department', string="Business Unit", tracking=True, domain=[
                                    ('layer_id.name', '=', 'Dep')], groups="employee_ext.group_hr_office_setup")
    office_type = fields.Selection([('operational', 'Operational'),
                                    ('semi_operational', 'Semi-Operational'),
                                    ('non_operational', 'Non-Operational')], string='Office Type', tracking=True, groups="employee_ext.group_hr_office_setup")
    currency = fields.Many2one('res.currency', string="Currency", tracking=True, groups="employee_ext.group_hr_office_setup")
    initial_exchange_rate = fields.Integer('Initial Exchange Rate', tracking=True, groups="employee_ext.group_hr_office_setup")
    status = fields.Selection([('current', 'Current'),
                               ('under_progress', 'Underprogress'),
                               ('will_terminated', 'Will be Terminated'),
                               ('terminated', 'Terminated'),
                               ('detached', 'Detached')], string='Status', tracking=True, groups="employee_ext.group_hr_office_setup")
    supervisor = fields.Many2one('hr.employee', string='Supervisor', tracking=True, groups="employee_ext.group_hr_office_setup")
    lease_start_date = fields.Date('Lease Start Date', tracking=True, groups="employee_ext.group_hr_office_setup")
    lease_end_date = fields.Date('Lease End Date', tracking=True, groups="employee_ext.group_hr_office_setup")
    request_start_date = fields.Date('Request Start Date', tracking=True, groups="employee_ext.group_hr_office_setup")
    office_approved_date = fields.Date('Office Approved Date', tracking=True, groups="employee_ext.group_hr_office_setup")
    office_move_in_date = fields.Date('Office Move In Date', tracking=True, groups="employee_ext.group_hr_office_setup")
    office_area = fields.Float("Office Area(Sqm)", compute="_compute_office_area_sqm", help="Based on square meters",
                               default=0, store=True, readonly=False, tracking=True, groups="employee_ext.group_hr_office_setup")
    office_area_sqft = fields.Float("Office Area(Sqft)", compute="_compute_office_area_sqft", help="Based on square feet",
                                    default=0, store=True, readonly=False, tracking=True, groups="employee_ext.group_hr_office_setup")
    seats = fields.Integer("Seats", default=0, tracking=True)
    occupied_seats = fields.Integer("Occupied Seats", compute="_compute_occupied_seats", default=0, store=True, readonly=True, tracking=True, precompute=True)
    vacant_seats = fields.Integer("Vacant Seats", compute="_compute_occupied_seats", default=0, store=True, readonly=True, tracking=True, precompute=True)
    occupied_percent = fields.Float("Occupied Percent", compute="_compute_occupied_seats", default=0, store=True, readonly=True, tracking=True, precompute=True)
    deposit_lc = fields.Float('Deposit LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    forex_impact_rate = fields.Float('Forex Impact Rate', tracking=True, groups="employee_ext.group_hr_office_setup")
    forex_deposit_lc = fields.Float('Forex Impact-HC Deposit LC', compute="_compute_hc_deposit",
                                    default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    fit_out_cost_lc = fields.Float('Fit-Out Cost LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    furniture_cost_lc = fields.Float('Furniture Cost LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    designer_fee_lc = fields.Float('Designer Fee LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    pantry_admin_lc = fields.Float('Pantry and Admin Supplies LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    it_cost_lc = fields.Float('IT Cost LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    commissions_extra_lc = fields.Float('Commissions & Extra LC', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    rent_lines = fields.One2many('hr.station.rent', 'station_id',string='Rent Lines', groups="employee_ext.group_hr_office_setup")
    deposit_lines = fields.One2many('hr.station.deposit', 'station_id',string='Deposit Lines', groups="employee_ext.group_hr_office_setup")
    deposit_usd = fields.Float('Deposit USD', tracking=True, digits=(15, 2), groups="employee_ext.group_hr_office_setup")
    forex_deposit_usd = fields.Float('Forex Impact-HC Deposit USD', compute="_compute_usd_values", default=0,
                                     store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    fit_out_cost_usd = fields.Float('Fit-Out Cost USD', compute="_compute_usd_values",
                                    default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    furniture_cost_usd = fields.Float('Furniture Cost USD', compute="_compute_usd_values",
                                      default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    designer_fee_usd = fields.Float('Furniture Cost USD', compute="_compute_usd_values", default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    pantry_admin_usd = fields.Integer('Pantry and Admin Supplies USD', compute="_compute_usd_values", default=0, store=True,
                                      tracking=True, groups="employee_ext.group_hr_office_setup")
    it_cost_usd = fields.Float('IT Cost USD', compute="_compute_usd_values", default=0,
                               store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    commissions_extra_usd = fields.Float('Commissions & Extra USD', compute="_compute_usd_values", default=0, store=True,
                                         tracking=True, groups="employee_ext.group_hr_office_setup")
    total_cost_lc = fields.Float('Total Cost LC', compute="compute_total_cost_lc",
                                 default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")
    total_cost_usd = fields.Float('Total Cost USD', compute="compute_total_cost_usd", default=0, store=True, tracking=True, groups="employee_ext.group_hr_office_setup")


    _sql_constraints = [
        ('date_check', "CHECK (lease_start_date <= lease_end_date)",
         "The start date must be before the end date."),
    ]

    def action_archive(self):
        for record in self:
            if len(record.public_emp_ids) > 0:
                raise ValidationError(_("You cannot archive station which has employee."))
        return super(WorkLocation, self).action_archive()
    
    def read(self, fields=None, load='_classic_read'):
        self._compute_occupied_seats()
        return super(WorkLocation, self).read(fields=fields, load=load)