# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime
import calendar
from dateutil.relativedelta import *
from odoo.exceptions import UserError, ValidationError

class reject_request(models.TransientModel):
	_name = "reject.request"
	_description = "Reject request message wizard"

	message = fields.Char("Message")

	def update_employee_to_reject_request(self):
		loan_id = False
		if 'loan_id' in self.env.context:
			loan_id = self.env['loan.request'].browse(self.env.context.get('loan_id'))
			template_id = self.env['ir.model.data']._xmlid_lookup('bi_hr_employee_loan.email_template_cancel_loan_request')[1]
			loan_id.update({
				'cancel_loan_employee_id' : self.env.user.id
				})
			email_template_obj = self.env['mail.template'].sudo().browse(template_id)
			if template_id:
				values = email_template_obj._generate_template(loan_id.ids,
				 	[
				 	'subject',
				 	'body_html',
				 	'email_from',
				 	'email_to',
				 	'partner_to',
				 	'email_cc',
				 	'reply_to',
				 	'scheduled_date',
				 	'res_id',
				 	])
				for res_id, val in list(values.items()):
					val['email_from'] = self.env.user.email
					val['email_to'] = loan_id.employee_id.work_email or loan_id.employee_id.user_id.email
					val['res_id'] = False
					val['is_notification'] = True
					mail_mail_obj = self.env['mail.mail']
					msg_id = mail_mail_obj.sudo().create(val)
					if msg_id:
						mail_mail_obj.send([msg_id])
				loan_id.update({
					'stage' : 'cancel'
					})