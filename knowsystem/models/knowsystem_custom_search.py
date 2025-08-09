# -*- coding: utf-8 -*-

from odoo import api, fields, models


class knowsystem_custom_search(models.Model):
    """
    The model to keep custom search values for portal
    """
    _name = "knowsystem.custom.search"
    _description = "Article Custom Search"

    @api.depends("custom_field_id.field_description")
    def _compute_name(self):
        """
        Compute method for name
        """
        for csearch in self:
            csearch.name = csearch.custom_field_id.field_description

    custom_field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        domain=[("model", "=", "knowsystem.article"), ("store", "=", True), ("ttype", "in", ["char", "text", "html"])],
        ondelete="cascade",
    )
    name = fields.Char("Label", required=True, compute=_compute_name, store=True, readonly=False)
