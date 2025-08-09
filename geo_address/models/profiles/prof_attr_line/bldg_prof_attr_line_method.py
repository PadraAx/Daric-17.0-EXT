# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class BuildingProfileAttributeLine(models.Model):
    _inherit = "bldg.profile.attribute.line"
