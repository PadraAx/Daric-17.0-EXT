# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api


class Slide(models.Model):
    _inherit = "slide.slide"

    content_doc_file_name = fields.Char('File Name')
