# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _


class HrCostCenter(models.Model):
    _name = "hr.cost.center"
    _description = "Cost Center"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'complete_name'
    _parent_store = True


    name = fields.Char(string="Name", required=True, tracking=True,)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, tracking=True,)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True, tracking=True,)
    active = fields.Boolean('Active', default=True, tracking=True,
                            help="By unchecking the active field, you may hide an version you will not use.")
    parent_id = fields.Many2one('hr.cost.center', string='Parent', index=True, tracking=True,
                                check_company=True, domain="[('id','!=', id)]")
    child_ids = fields.One2many('hr.cost.center', 'parent_id', string='Child Cost Center', tracking=True,)
    parent_path = fields.Char(index=True, unaccent=False, tracking=True,)
    master_department_id = fields.Many2one('hr.cost.center', 'Master Cost Center', tracking=True,
                                           compute='_compute_master_department_id', store=True)
    total_subordinates = fields.Integer(compute='_compute_total_subordinates', string='Total Subordinates', tracking=True,)
    employee_cost_center = fields.One2many(
        'hr.employee.cost.center', 'cost_center_id', string='Employee Ids', readonly=True, tracking=True,)


    @api.depends('total_subordinates')
    def _compute_total_subordinates(self):
        for record in self:
            record.total_subordinates = len(record.child_ids)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for center in self:
            if center.parent_id:
                center.complete_name = '%s / %s' % (center.parent_id.complete_name, center.name)
            else:
                center.complete_name = center.name

    @api.depends('parent_path')
    def _compute_master_department_id(self):
        for center in self:
            center.master_department_id = int(center.parent_path.split('/')[0])

    def cost_center_childs_action(self):
        return {
            'name': self.complete_name,
            'res_model': 'hr.cost.center',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
        }


class HrEmployeeCostCenter(models.Model):
    _name = 'hr.employee.cost.center'
    _description = 'Employee Cost Center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'eff_date desc'


    employee_id = fields.Many2one('hr.employee', string="employee", tracking=True)
    cost_center_id = fields.Many2one('hr.cost.center', string="Cost Center", tracking=True)
    eff_date = fields.Date(string="Effective Date", default=lambda self: datetime.today(), tracking=True)
    percent = fields.Float(string="Percent", default=0, digits=(4, 2), tracking=True)
    active_status = fields.Boolean(string="Active", default=True, tracking=True)


    def action_save(self):
        pass 
    
    def action_delete(self):
        self.unlink() 
    
    def open_record(self):
        if self.env.user.has_group('employee_ext.group_hr_organization_development'):
            return {
                'name': _('Employee Cost Center'),
                'target': 'new',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.employee.cost.center',
                'view_id': self.env.ref('employee_ext.view_hr_employee_cost_center_form').id,
                'res_id': self.id,
                }