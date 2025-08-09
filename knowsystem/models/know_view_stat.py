# -*- coding: utf-8 -*-

from odoo import api, fields, models


class know_view_stat(models.Model):
    """
    The model to systemize article tags
    """
    _name = "know.view.stat"
    _description = "View Stats"
    _rec_name = "user_id"

    @api.depends("user_id.name", "counter")
    def _compute_display_name(self):
        """
        Compute method for display_name
        """
        for stat in self:
            stat.display_name = "{} ({})".format(stat.user_id.name, stat.counter)

    user_id = fields.Many2one("res.users", "User")
    counter = fields.Integer(string="Number")
