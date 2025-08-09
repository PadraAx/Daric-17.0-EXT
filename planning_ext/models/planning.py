# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from datetime import date, datetime
import pytz
from odoo.osv import expression


class Planning(models.Model):
    _inherit = 'planning.slot'


    @api.constrains('extend')
    def check_extend(self):
        for record in self:
            if record.extend < 0:
                raise ValidationError("Shenavari should bigger than zero")
            if record.extend > 60:
                raise ValidationError("Shenavari should smaller than sixty")


    extend = fields.Integer(string="Shenavari", default=30)
    
    
    # ----------------------------------------------------
    # Business Methods
    # ----------------------------------------------------

    def _calculate_slot_duration(self):
        self.ensure_one()
        if not self.start_datetime or not self.end_datetime:
            return 0.0
        period = self.end_datetime - self.start_datetime
        slot_duration = period.total_seconds() / 3600
        return slot_duration
    
    
    @api.constrains('start_datetime', 'end_datetime')
    def _check_period(self):
        for planning in self:
            periods = self.env['hr.payroll.period'].search([('date_to', '>=', planning['start_datetime']),('date_from', '<=', planning['end_datetime'])])
            if periods.filtered(lambda item: item.status != 'open'):
                raise AccessError(_("This payroll period has been closed. You cannot change related records."))
            

    @api.depends('start_datetime', 'end_datetime', 'resource_id.calendar_id','company_id.resource_calendar_id', 'allocated_percentage')
    def _compute_allocated_hours(self):
        percentage_field = self._fields['allocated_percentage']
        self.env.remove_to_compute(percentage_field, self)
        for slot in self:
            # for each planning slot, compute the duration
            if slot.allocation_type != 'planning':
                raise AccessError(_("Planning shouldn't be more than 24 hours."))
            ratio = slot.allocated_percentage / 100.0
            slot.allocated_hours = slot._calculate_slot_duration() * ratio

                
    @api.model_create_multi
    def create(self, vals_list):
        Resource = self.env['resource.resource']
        for vals in vals_list:
            if vals.get('resource_id'):
                resource = Resource.browse(vals.get('resource_id'))
                if not vals.get('company_id'):
                    vals['company_id'] = resource.company_id.id
                if resource.resource_type == 'material':
                    vals['state'] = 'published'
            if not vals.get('company_id'):
                vals['company_id'] = self.env.company.id
        return super().create(vals_list)
    

    def write(self, values): 
        new_resource = self.env['resource.resource'].browse(values['resource_id']) if 'resource_id' in values else None
        if new_resource and new_resource.resource_type == 'material':
            values['state'] = 'published'
        # if the resource_id is changed while the shift has already been published and the resource is human, that means that the shift has been re-assigned
        # and thus we should send the email about the shift re-assignment
        if (new_resource and self.state == 'published'
                and self.resource_type == 'user'
                and new_resource.resource_type == 'user'):
            self._send_shift_assigned(self, new_resource)
        # if the "resource_id" or the "start/end_datetime" fields meaningfully change when there is a request to switch, remove the request to switch
        for slot in self:
            if slot.state == 'published' and 'state' not in values and 'hr.leave.model' not in slot._context:
                raise AccessError(_("Do not have access, this plan has been published."))
            if slot.request_to_switch and (
                (new_resource and slot.resource_id != new_resource)
                or ('start_datetime' in values and slot.start_datetime != datetime.strptime(values['start_datetime'], '%Y-%m-%d %H:%M:%S'))
                or ('end_datetime' in values and slot.end_datetime != datetime.strptime(values['end_datetime'], '%Y-%m-%d %H:%M:%S'))
            ):
                values['request_to_switch'] = False
        # update other slots in recurrency
        slots = self
        recurrence_update = values.pop('recurrence_update', 'this')
        if recurrence_update != 'this':
            recurrence_domain = []
            if recurrence_update == 'subsequent':
                for slot in self:
                    recurrence_domain = expression.OR([recurrence_domain,
                        ['&', ('recurrency_id', '=', slot.recurrency_id.id), ('start_datetime', '>=', slot.start_datetime)]
                    ])
            else:
                recurrence_domain = [('recurrency_id', 'in', self.recurrency_id.ids)]
            slots |= self.search(recurrence_domain)

        result = super(Planning, slots).write(values)
        # recurrence
        if any(key in ('repeat', 'repeat_unit', 'repeat_type', 'repeat_until', 'repeat_interval', 'repeat_number') for key in values):
            # User is trying to change this record's recurrence so we delete future slots belonging to recurrence A
            # and we create recurrence B from now on w/ the new parameters
            for slot in self:
                recurrence = slot.recurrency_id
                if recurrence and values.get('repeat') is None:
                    repeat_type = values.get('repeat_type') or recurrence.repeat_type
                    repeat_until = values.get('repeat_until') or recurrence.repeat_until
                    repeat_number = values.get('repeat_number', 0) or slot.repeat_number
                    if repeat_type == 'until':
                        repeat_until = datetime.combine(fields.Date.to_date(repeat_until), datetime.max.time())
                        repeat_until = repeat_until.replace(tzinfo=pytz.timezone(slot.company_id.resource_calendar_id.tz or 'UTC')).astimezone(pytz.utc).replace(tzinfo=None)
                    recurrency_values = {
                        'repeat_interval': values.get('repeat_interval') or recurrence.repeat_interval,
                        'repeat_unit': values.get('repeat_unit') or recurrence.repeat_unit,
                        'repeat_until': repeat_until if repeat_type == 'until' else False,
                        'repeat_number': repeat_number,
                        'repeat_type': repeat_type,
                        'company_id': slot.company_id.id,
                    }
                    recurrence.write(recurrency_values)
                    if slot.repeat_type == 'x_times':
                        recurrency_values['repeat_until'] = recurrence._get_recurrence_last_datetime()
                    end_datetime = slot.end_datetime if values.get('repeat_unit') else recurrency_values.get('repeat_until')
                    recurrence._delete_slot(end_datetime)
                    recurrence._repeat_slot()
        return result
    
    def unlink(self):      
        self._check_period()
        return super(Planning, self).unlink()
