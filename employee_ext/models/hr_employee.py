# -*- coding: utf-8 -*-

from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

EMP_DEP_QUERY = '''
WITH RECURSIVE department_hierarchy AS (
    SELECT 
        d.id AS department_id, 
        d.parent_id, 
        (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS department_name, 
        d.layer_id,
        (SELECT name FROM hr_department_layer WHERE id = d.layer_id) AS layer_name
    FROM hr_department d
    where id = %s
    UNION ALL
    SELECT 
        d.id AS department_id, 
        d.parent_id, 
        (SELECT value FROM jsonb_each_text(d.name) LIMIT 1) AS department_name, 
        d.layer_id,
        (SELECT name FROM hr_department_layer WHERE id = d.layer_id) AS layer_name
    FROM hr_department d
    INNER JOIN department_hierarchy dh ON dh.parent_id = d.id
)

-- Pivot the results to show each layer_name as a separate column
SELECT 
    MAX(CASE WHEN layer_id = 1 THEN department_name END) AS "division", 
    MAX(CASE WHEN layer_id = 2 THEN department_name END) AS "dep",
    MAX(CASE WHEN layer_id = 3 THEN department_name END) AS "unit",
    MAX(CASE WHEN layer_id = 4 THEN department_name END) AS "sub_unit",
    MAX(CASE WHEN layer_id = 5 THEN department_name END) AS "desk",
    MAX(CASE WHEN layer_id = 1 THEN department_id END) AS "division_id", 
    MAX(CASE WHEN layer_id = 2 THEN department_id END) AS "dep_id",
    MAX(CASE WHEN layer_id = 3 THEN department_id END) AS "unit_id",
    MAX(CASE WHEN layer_id = 4 THEN department_id END) AS "sub_unit_id",
    MAX(CASE WHEN layer_id = 5 THEN department_id END) AS "desk_id"
FROM department_hierarchy
'''

contract_fields = ['job_id', 'department_id', 'resource_calendar_id',
                   'company_id', 'dependent_number', 'marital',
                   'childeren_dependent', 'probationary_period', 'notice_period',
                   'manager_id', 'legal_company', 'responsible_company',
                   'payment_type', 'employee_status', 'join_date']


UNIT_DICT = {
    'Dep': 'department_dep_id',
    'Division': 'department_division_id',
    'Unit': 'department_unit_id',
    'Sub Unit': 'department_subunit_id',
    'Desk': 'department_desk_id',
}


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'
    _order = 'sequence, name'
    _sql_constraints = []


    @api.model
    def _lang_get(self):
        return self.env['res.lang'].get_installed()

    # @api.onchange('company_id')
    # def _compute_address_id(self):
    #     for employee in self:
    #         if employee.company_id.id != employee.address_id.company_id.id:
    #             employee.address_id = False

    @api.onchange('address_id')
    def onchange_station(self):
        self.work_location_id = False

    @api.onchange('department_id')
    def onchange_job(self):
        self.job_id = False

    def return_employment_type(self):
        return [('full_time', 'Full Time'),
                ('part_time', 'Part Time'),
                ('consultant', 'Consultant'), ]

    @api.model
    def default_get(self, fields):
        res = super(HrEmployee, self).default_get(fields)
        res['employee_type'] = False
        return res

    @api.constrains('active')
    def check_employee_active(self):
        for emp in self:
            if not emp.active:
                emp.job_id.employee_id = False
                # emp.job_id = False

    def _get_running_contract(self):
        for record in self:
            record.running_contract = False
            if self.env['hr.contract'].sudo().search([('employee_id', '=', record.id), ('state', '=', 'open')]):
                record.running_contract = True

    @api.depends('work_contact_id', 'work_contact_id.email')
    def _compute_work_contact_details(self):
        for employee in self:
            if employee.work_contact_id:
                employee.work_email = employee.work_contact_id.email

    @api.depends('department_id')
    def _calculate_department_layers(self):
        # self.env.cr.execute("""select employee_id, dep, division, unit, sub_unit, desk from hr_emp_dep_layer_view where employee_id in (%s)""", (self.ids))
        # res = self.env.cr.dictfetchall()
        # out = {record['employee_id']:record for record in res}
        for employee in self:
            self.env.cr.execute(EMP_DEP_QUERY, (employee.department_id.id or 0,))
            res = self.env.cr.dictfetchone()
            employee.department_dep_id = res.get('dep', False)
            employee.department_division_id = res.get('division', False)
            employee.department_unit_id = res.get('unit', False)
            employee.department_subunit_id = res.get('sub_unit', False)
            employee.department_desk_id = res.get('desk', False)
        # for employee in self:
        #     for dep_field in UNIT_DICT.values():
        #         setattr(employee, dep_field, False)
        #     if employee.department_id:
        #         dep_obj = employee.department_id
        #         while dep_obj:
        #             if UNIT_DICT.get(dep_obj.layer_id.name):
        #                 setattr(employee, UNIT_DICT[dep_obj.layer_id.name], dep_obj.name)
        #             dep_obj = dep_obj.parent_id

    @api.constrains('national_code')
    def _check_unique_national_code(self):
        for record in self:
            if record.national_code:
                existing_national_code = self.search([
                    ('national_code', '=', record.national_code),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_national_code:
                    raise ValidationError("National code must be unique.")

    @api.constrains('insurance_number')
    def _check_unique_insurance_number(self):
        for record in self:
            if record.insurance_number:
                existing_insurance_number = self.search([
                    ('insurance_number', '=', record.insurance_number),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_insurance_number:
                    raise ValidationError("Insurance number must be unique.")

    @api.constrains('personnel_code')
    def _check_unique_personnel_code(self):
        for record in self:
            if record.personnel_code:
                existing_personnel_code = self.search([
                    ('personnel_code', '=', record.personnel_code),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing_personnel_code:
                    raise ValidationError("Personnel code must be unique.")

    @api.constrains('parent_id')
    def distinct_employee_manager(self):
        for record in self:
            this = record.sudo()
            if this.parent_id.id == record.id:
                raise ValidationError("Manager field should be different from the employee.")
            if this.parent_id and not this.parent_id.user_id.id:
                raise ValidationError("This manager doesn't have related user so time off approver field is null. First set manager's user")
            record.leave_manager_id = this.parent_id.user_id.id 
    
    @api.constrains('user_id')
    def related_user_change(self):
        for record in self:
            record.child_ids.write({'leave_manager_id': record.user_id.id})
            
    @api.constrains('job_id')
    def check_employee_job(self):
        for emp in self:
            self.env['hr.job'].search([('employee_id', '=', emp.id)]).write({'employee_id': False})
            if emp.job_id:
                emp.job_id.employee_id = emp.id


    active = fields.Boolean('Active', related='resource_id.active', default=True,
                            store=True, readonly=False, tracking=True)
    name = fields.Char(string="Employee Name", related='resource_id.name', store=True, readonly=False, tracking=True)
    job_id = fields.Many2one(
        tracking=True, domain="[('employee_id','=', False), ('department_id', '=', department_id)]", check_company=False, copy=False)
    message_main_attachment_id = fields.Many2one(groups="base.group_user")
    marital = fields.Selection([('single', 'Single'),
                                ('married', 'Married'),
                                ('widower', 'Widower'),
                                ('divorced', 'Divorced')], string='Marital Status', default='single', tracking=True, groups=None)
    country_id = fields.Many2one('res.country', 'Nationality (Country)', tracking=True, groups=None)
    emergency_contact = fields.Char("Contact Name", tracking=True, groups=None)
    emergency_phone = fields.Char("Emergency Contact No", tracking=True, groups=None,)
    private_street = fields.Char(string="Permanent Address", groups=None, tracking=True,)
    private_phone = fields.Char(string="Personal Contact No.", groups=None, tracking=True,)
    private_email = fields.Char(string="Personal Email", groups=None, tracking=True,)
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female'),
                               ('other', 'Other')], tracking=True, groups=None)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", tracking=True, groups=None)
    birthday = fields.Date('Date of Birth', tracking=True, groups=None)
    passport_id = fields.Char('Passport No', tracking=True, groups=None)
    visa_no = fields.Char('Visa No', tracking=True, groups=None)
    visa_expire = fields.Date('Visa Expire Date', tracking=True, groups=None)
    permit_no = fields.Char('Work Permit No', groups=None, tracking=True)
    work_permit_expiration_date = fields.Date('Work Permit Expiration Date', tracking=True, groups=None)
    mobile_phone = fields.Char('Work Mobile', compute="False",
                               store=True, inverse='_inverse_work_contact_details', tracking=True)
    work_phone = fields.Char('Work Phone', compute="_compute_phones", store=True, readonly=False, tracking=True)
    work_email = fields.Char('Work Email', compute="_compute_work_contact_details", store=True,
                             inverse='_inverse_work_contact_details', tracking=True)
    place_of_birth = fields.Char('Place of Birth', groups=None, tracking=True)
    is_non_resident = fields.Boolean(string='Non-resident', help='If recipient lives in a foreign country', groups=None)
    employee_type = fields.Selection(selection=return_employment_type, string='Employee Type', groups="base.group_user", default=None, required=False, tracking=True,
                                     help="The employee type. Although the primary purpose may seem to categorize employees, this field has also an impact in the Contract History. Only Employee type is supposed to be under contract and will have a Contract History.")
    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account Number', domain="[('partner_id', '=', work_contact_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                      groups=None, tracking=True, help='Employee bank account to pay salaries')
    departure_date = fields.Date(string="Departure Date", groups=None, copy=False, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=None, groups="base.group_user", tracking=True,)
    company_country_id = fields.Many2one(related="company_id.country_id")
    address_id = fields.Many2one('res.partner', string='Work Address',
                                 compute=False, tracking=True, store=True, readonly=False, check_company=True)
    work_location_id = fields.Many2one('hr.work.location', 'Station',
                                       domain="[('address_id', '=', address_id)]", tracking=True, ondelete='restrict')
    ssnid = fields.Char('SSN No', help='Social Security Number', groups=None, tracking=True)
    pin = fields.Char(string="PIN", groups=None, copy=False,
                      help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")
    children = fields.Integer(string='Number of Children', groups=None, tracking=True, default=0)
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups=None, copy=False)
    child_ids = fields.One2many('hr.employee', 'parent_id', string='Direct subordinates',
                                check_company=True, tracking=True)
    resource_calendar_id = fields.Many2one('resource.calendar', check_company=False, domain=[], default=lambda self: self.env.company.resource_calendar_id.id)
    parent_id = fields.Many2one('hr.employee', 'Manager', compute=False, tracking=True,
                                store=True, readonly=False, check_company=False)
    contract_warning = fields.Boolean(string='Contract Warning', store=True,
                                      compute='_compute_contract_warning', groups=None)
    user_id = fields.Many2one(tracking=True)
    # EXTRA FIELDS
    first_name = fields.Char(size=128, string="First Name", required=False, tracking=True,)
    last_name = fields.Char(size=128, string="Last Name", required=False, tracking=True,)
    personnel_code = fields.Char(string="Personnel Code", required=False, tracking=True, copy=False)
    home_country_address_id = fields.Char(string="Home Country Address", tracking=True)
    labour_personal_code = fields.Char('Labor Personal Code', size=128, tracking=True,)
    residential_status = fields.Selection(string='Residential Status', selection=[('local', 'Local'),
                                                                                  ('expat', 'Expat')], tracking=True,)
    employee_status = fields.Selection(string='Employee Status', selection=[('probation', 'Probation'),
                                                                            ('extended_probation', 'Extended Probation'),
                                                                            ('confirmed', 'Confirmed')], tracking=True,)
    contract_id = fields.Many2one('hr.contract', string='Current Contract', groups=None, tracking=True,
                                  domain="[('company_id', '=', company_id), ('employee_id', '=', id)]", help='Current contract of the employee')
    warning_letter_ids = fields.One2many('hr.employee.warning.letter', 'employee_id', string='Notice Letter')
    education_ids = fields.One2many('hr.employee.education', 'employee_id', string='Employee Education')
    termination_ids = fields.One2many('hr.employee.termination', 'employee_id', string='Employee Termination')
    document_ids = fields.One2many('hr.employee.document', 'employee_id', string='Work Document')
    dependent_ids = fields.One2many('hr.employee.dependent', 'employee_id', string='Employee Dependent')
    identification_id = fields.Char(string='Identification Number', tracking=True, groups=None)
    training_ids = fields.One2many('hr.employee.training', 'employee_id', string='Training Profile')
    contact_id = fields.One2many('hr.employee.contact', 'employee_id', string='Contact')
    achievement_id = fields.One2many('hr.employee.achievement', 'employee_id', string='Achievements')
    cost_center_ids = fields.One2many('hr.employee.cost.center', 'employee_id', string='Cost Center')
    payment_type = fields.Many2one('hr.employee.payment.type', string='Payment Type', tracking=True,)
    indirect_manager = fields.Many2one('hr.employee', 'Indirect Manager', tracking=True,
                                       domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    leader_in_function = fields.Many2many('hr.employee', 'leader_employee_assigned',
                                          'employee_id', 'leader_id', 'Leader In Function', tracking=True)
    personal_assist = fields.Many2many('hr.employee', 'assist_employee_assigned',
                                       'employee_id', 'assist_id', 'Personal Assist', tracking=True)
    nationality = fields.Char(string='Nationality', tracking=True)
    other_nationality = fields.Char(string='Other Nationality', tracking=True)
    department_id = fields.Many2one(tracking=True, check_company=False)
    department_dep_id = fields.Char(
        string='Department', compute="_calculate_department_layers", store=True, tracking=True)
    department_division_id = fields.Char(
        string='Division', compute="_calculate_department_layers", store=True, tracking=True)
    department_unit_id = fields.Char(string='Unit', compute="_calculate_department_layers", store=True, tracking=True)
    department_subunit_id = fields.Char(
        string='Sub-Unit', compute="_calculate_department_layers", store=True, tracking=True)
    department_desk_id = fields.Char(string='Desk', compute="_calculate_department_layers", store=True, tracking=True)
    join_date = fields.Date('Join Date', tracking=True, )
    termination_date = fields.Date('Termination Date', tracking=True, )
    national_code = fields.Char('National Code', required=False, tracking=True, copy=False)
    sequence = fields.Integer('sequence', default=1, tracking=True,)
    id_expire_date = fields.Date(string="ID Expire Date", tracking=True,)
    passport_expire_date = fields.Date(string="Passport Expire Date", tracking=True,)
    type_of_permit = fields.Selection(string='Type of Permit', selection=[('employment_pass', 'Employment Pass'),
                                                                          ('citizen', 'Citizen'),
                                                                          ('Permanent_resident', 'Permanent Resident')], tracking=True,)
    resume = fields.Binary(string='Resume')
    filename = fields.Char('File Name')
    religion = fields.Many2one('hr.religion', string='Religion', tracking=True)
    pan_card_no = fields.Char('Pan Card No', tracking=True)
    pf_no = fields.Char('PF No', tracking=True)
    pf_uan_no = fields.Char('PF UAN No', tracking=True)
    sss_no = fields.Char('SSS No', tracking=True)
    bir_no = fields.Char('BIR No', tracking=True)
    hdmf_no = fields.Char('HDMF No', tracking=True)
    emergency_address = fields.Char(string="Emergency Address", tracking=True)
    emergency_relation = fields.Many2one('hr.relationship.type', string="Relation", tracking=True)
    emergency_email = fields.Char(string="Emergency Email", tracking=True,)
    dependent_number = fields.Integer(string="Number of Dependent", tracking=True, default=0)
    phil_health_no = fields.Integer(string="Phil Health No", tracking=True)
    legal_company = fields.Many2one('res.company', string="Legal Entity", tracking=True)
    responsible_company = fields.Many2one('res.company', string="Responsible Company", required=True, tracking=True)
    running_contract = fields.Boolean(compute='_get_running_contract', string='Running Contract')
    second_phone = fields.Char(string="Home Country Contact No.", groups=None, tracking=True,)
    lang = fields.Selection(selection=_lang_get, string="Lang", groups=None, tracking=True,)
    # account fields
    bank_name = fields.Char(string="Bank Name", tracking=True)
    bank_account = fields.Char(string="Bank Account No", tracking=True)
    swift_code = fields.Char(string="Swift Code", tracking=True)
    branch_location = fields.Char(string="Branch/Location", tracking=True)
    iban_no = fields.Char(string="IBAN No", tracking=True)
    ifsc_code = fields.Char(string="IFSC Code", tracking=True)
    # insurance fields
    father_name = fields.Char(size=128, string="Father Name", tracking=True,)
    mother_name = fields.Char(size=128, string="Mother Name", tracking=True,)
    insurance_number = fields.Char(string="Insurance Number", required=False, tracking=True, copy=False)
    tamin_job_id = fields.Many2one('hr.tamin.job', 'Insurance Job Title', tracking=True,)
    probationary_period = fields.Integer(string="Probationary Period", tracking=True)
    notice_period = fields.Integer(string="Notice Period", tracking=True)
    local_first_name = fields.Char(size=128, string="First Name", tracking=True)
    local_last_name = fields.Char(size=128, string="Last Name", tracking=True,)
    Local_father_name = fields.Char(size=128, string="Father Name", tracking=True,)
    local_job_position = fields.Char(string="Job Position", tracking=True,)
    local_address = fields.Char(string="Local Address", tracking=True)
    local_birth_place = fields.Char(string='Birth Place', tracking=True)
    local_nationality = fields.Char(string='Nationality', tracking=True)
    local_degree = fields.Char(string='Degree of Education', tracking=True)
    departure_description = fields.Html(string="Additional Information",
                                        groups="hr.group_hr_user", copy=False, tracking=False)



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('personnel_code'):
                vals['personnel_code'] = self.env['ir.sequence'].next_by_code('personnel.code')
        return super().create(vals_list)

    def unlink(self):
        is_parent = self.search([('parent_id', 'in', self.ids), ('active', '=', True)])
        if is_parent:
            raise ValidationError("You cannot delete an employee who is someone's manager.")
        # to remove job reference after unlink process
        emp_ids = self.ids
        res = super().unlink()
        self.env['hr.job'].search([('employee_id', 'in', emp_ids)]).write({'employee_id': False})

    def write(self, vals):
        for record in self:
            # check contract running
            if record.running_contract and not self._context.get('from_running_contract'):
                if any([item in contract_fields for item in vals.keys()]):
                    raise ValidationError("You cannot change running contract values.")
            # change time off approver when we change manager
            # if vals.get('parent_id'):
            #     vals['leave_manager_id'] = self.search([('id', '=', vals['parent_id'])]).user_id.id
            # change all related time off approver when we change user_id
            # if 'user_id' in vals:
            #     self.search([('leave_manager_id', '=', record.user_id.id)]).write({'leave_manager_id': vals['user_id']})
        return super(HrEmployee, self).write(vals)

    def create_cost_center(self):
        return {
            'name': _('Employee Cost Center'),
            'target': 'new',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.employee.cost.center',
            'view_id': self.env.ref('employee_ext.view_hr_employee_cost_center_form').id,
            'context': {
                'default_employee_id': self.id,
            }
        }

    def action_archive(self):
        for record in self:
            if len(record.child_ids) > 0:
                raise ValidationError(_("You cannot archive employee who has subordinates because their managers will be empty."))
        return super(HrEmployee, self).action_archive()    
        

    # def read(self, fields=None, load='_classic_read'):
    #     res = super(HrEmployee, self).read(fields=fields, load=load)
    #     self.search([])._calculate_department_layers()
    #     return res
