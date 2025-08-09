# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WebsiteFAQ(models.Model):
	_name = 'website.faq'
	_description = 'Website FAQ'

	is_published = fields.Boolean(string="Website Published ?");
	name = fields.Text(string="Question");
	answer = fields.Html(string="Answer");



class Ir_attachment(models.Model):
	_inherit = "ir.attachment"
	_description = "Inherited Ir Attachment to Validation"


	def check(self, mode, values=None):
		if not self.ids and mode=="write" and 'name' not in values:
			raise ValidationError("Image error \nPlease select image");
		else:
			return super(Ir_attachment,self).check(mode, values);




	




