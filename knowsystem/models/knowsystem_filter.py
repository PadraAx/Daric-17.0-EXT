# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class knowsystem_filter(models.Model):
    """
    The model to apply articles for definite Odoo documents
    """
    _name = "knowsystem.filter"
    _description = "Document Filter"

    @api.depends("model", "tag_id.name")
    @api.depends_context("lang")
    def _compute_display_name(self):
        """
        Compute method for display_name
        """
        for doc_filter in self:
            doc_filter.display_name = "{} ({})".format(
                doc_filter.model, doc_filter.tag_id and doc_filter.tag_id.name or ""
            )

    @api.depends("ir_model_id")
    def _compute_domain(self):
        """
        Compute method for domain to clear it when the model is changed
        """
        for doc_filter in self:
            doc_filter.domain = "[]"

    ir_model_id = fields.Many2one("ir.model", string="Model")
    model = fields.Char(string="Model Name", related="ir_model_id.model", related_sudo=True, compute_sudo=True)
    domain = fields.Text(
        string="Applied Filters", compute=_compute_domain, store=True, readonly=False, required=True, default="[]",
    )
    tag_id = fields.Many2one("knowsystem.tag", string="Tag")

    @api.model
    def _check_document(self, res_id):
        """
        The method to check whether this document suits this filter

        Args:
         * res_id - id of the document

        Returns:
         * bool
        """
        domain = [("id", "=", res_id)]
        filter_domain = self.domain and safe_eval(self.domain) or []
        domain += filter_domain
        suits = self.env[self.model].search(domain, limit=1)
        return suits and True or False
