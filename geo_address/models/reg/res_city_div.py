# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from odoo.tools import image_process
import logging

_logger = logging.getLogger(__name__)


class CityDivision(models.Model):
    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _name = "res.city.div"
    _description = "City Division"
    _order = "hierarchical_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _parent_store = True
    _rec_name = "name"
    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # Descriptive Fields
    # ============================================
    name = fields.Char(required=True, tracking=True)
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=True,
        prefetch=False,
        help="Detailed description of the village",
    )
    # ============================================
    # External Relational Fields
    # ============================================
    city_id = fields.Many2one(
        "res.city", required=True, ondelete="cascade", index=True, tracking=True
    )
    bldg_ids = fields.One2many(
        "bldg.building", "city_div_id", string="Buildings in This Division"
    )
    # ============================================
    # Internal Relational Fields
    # ============================================
    full_path = fields.Char(
        compute="_compute_full_path", store=True, recursive=True, string="Full Path"
    )
    parent_path = fields.Char(index=True)
    parent_id = fields.Many2one(
        "res.city.div",
        ondelete="cascade",
        domain="[('city_id', '=', city_id)]",
        index=True,
        tracking=True,
    )
    generation = fields.Integer(
        string="Generation", compute="_compute_generation", store=True
    )
    sibling_count = fields.Integer(
        string="Siblings in Same Generation", compute="_compute_sibling_count"
    )
    child_ids = fields.One2many("res.city.div", "parent_id", string="Child Divisions")
    # ============================================
    # Media Fields
    # ============================================
    profile_image = fields.Image(
        string="Profile Image",
        max_width=256,
        max_height=256,
        help="Main image for this division",
        attachment=True,
    )
    profile_image_thumbnail = fields.Image(
        "Thumbnail", related="profile_image", max_width=128, max_height=128, store=True
    )
    attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        domain=lambda self: [
            ("res_model", "=", self._name),
            (
                "mimetype",
                "in",
                [
                    "image/jpeg",
                    "image/png",
                    "image/gif",
                    "video/mp4",
                    "video/webm",
                    "application/pdf",
                ],
            ),
        ],
        string="Media Gallery",
    )
    gallery_count = fields.Integer(
        compute="_compute_gallery_count", string="Media Items"
    )
    # ============================================
    # Identification Fields
    # ============================================

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        readonly=True,
        copy=False,
        index=True,
        help="Format: [CountryCode]-[CitySystemID]-[DivisionID]",
    )

    sequence = fields.Integer(string="Sequence", default=10)
    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = [
        (
            "unique_hierarchical_id",
            "unique(hierarchical_id)",
            "Hierarchical ID must be unique.",
        )
    ]

    _index = [
        ("parent_path", "btree"),
        ("city_id", "btree"),
        ("generation", "btree"),
        ("hierarchical_id", "btree"),
        ("parent_id", "btree"),
        (("city_id", "parent_id"), "btree"),
    ]

    # ==========================================================================
    # Methods
    # ==========================================================================
    # ============================================
    # Descriptive Fields Related Methods
    # ============================================
    def name_get(self):
        """Display name showing full path with fallback"""
        result = []
        for rec in self:
            name = rec.full_path or f"{rec.city_id.name or ''} / {rec.name}"
            result.append((rec.id, name))
        return result

    # ============================================
    # Internal Relational Fields Related Methods
    # ============================================
    def _get_all_children(self):
        """Get all descendants of this division"""
        return self.search([("parent_path", "=like", f"{self.parent_path}%")])

    @api.depends("parent_id")
    def _compute_generation(self):
        for rec in self:
            if rec.parent_id:
                rec.generation = rec.parent_id.generation + 1
            else:
                rec.generation = 1

    @api.depends("parent_id", "city_id")
    def _compute_sibling_count(self):
        for rec in self:
            # Avoid computing for unsaved records
            if not isinstance(rec.id, int):
                rec.sibling_count = 0
                continue

            domain = [
                ("city_id", "=", rec.city_id.id),
                ("parent_id", "=", rec.parent_id.id if rec.parent_id else False),
                ("id", "!=", rec.id),
            ]
            rec.sibling_count = self.search_count(domain) + 1

    @api.depends("name", "parent_id.full_path", "city_id.name")
    def _compute_full_path(self):
        """Compute the full hierarchical path with caching"""
        for rec in self:
            if rec.parent_id:
                rec.full_path = f"{rec.parent_id.full_path} / {rec.name}"
            else:
                rec.full_path = f"{rec.city_id.name or ''} / {rec.name}"

    # ============================================
    # Media Fields Related Methods
    # ============================================
    @api.depends("attachment_ids")
    def _compute_gallery_count(self):
        """Count media items"""
        for rec in self:
            rec.gallery_count = len(rec.attachment_ids)

    def add_to_gallery(self, media_type, **kwargs):
        """Add media to gallery with type-specific handling using Odoo's attachment system"""
        self.ensure_one()

        file_data = kwargs.get("file_data")
        name = kwargs.get("name", "Untitled Media")
        mimetype = kwargs.get("mimetype")

        if not mimetype:
            if media_type == "image":
                mimetype = "image/jpeg"
            elif media_type == "video":
                mimetype = "video/mp4"
            elif media_type == "document":
                mimetype = "application/pdf"

        return self.env["ir.attachment"].create(
            {
                "name": name,
                "type": "binary",
                "datas": file_data,
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": mimetype,
            }
        )

    def open_media(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Media",
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [("res_model", "=", self._name), ("res_id", "=", self.id)],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }

    def action_view_media(self):
        """Action to view media attachments for this division"""
        self.ensure_one()
        return {
            "name": _("Media Gallery"),
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "view_mode": "kanban,tree,form",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("mimetype", "ilike", "image/%"),
            ],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
                "search_default_filter_images": True,
            },
        }

    # ============================================
    # CRUD Methods
    # ============================================
    @api.model_create_multi
    def create(self, vals_list):
        # Group records by city_id
        grouped_by_city = {}
        for vals in vals_list:
            city_id = vals.get("city_id")
            if city_id:
                grouped_by_city.setdefault(city_id, []).append(vals)
            else:
                vals["hierarchical_id"] = False

        for city_id, records_for_city in grouped_by_city.items():
            city = self.env["res.city"].browse(city_id)
            city_hier_id = city.hierarchical_id

            # Skip if city has invalid hierarchical_id format
            if not city_hier_id or not city_hier_id.endswith("000"):
                for vals in records_for_city:
                    vals["hierarchical_id"] = False
                continue

            prefix = city_hier_id[:-3]  # Get prefix (e.g., "US-NY-" from "US-NY-000")

            # First renumber ALL existing divisions in this city
            existing_divisions = self.search([("city_id", "=", city_id)], order="id")
            for index, div in enumerate(existing_divisions, start=1):
                div.hierarchical_id = f"{prefix}{index:03d}"

            # Now assign numbers to new records (continuing from existing count)
            base_index = len(existing_divisions)
            for i, vals in enumerate(records_for_city, start=1):
                vals["hierarchical_id"] = f"{prefix}{(base_index + i):03d}"

        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)

        if "city_id" in vals:
            for rec in self:
                if not rec.city_id or not rec.city_id.hierarchical_id.endswith("000"):
                    rec.hierarchical_id = False
                    continue

                prefix = rec.city_id.hierarchical_id[:-3]

                # Avoid race condition: use SQL
                self.env.cr.execute(
                    """
                    SELECT MAX(CAST(SUBSTRING(hierarchical_id FROM LENGTH(%s)+1 FOR 3) AS INTEGER))
                    FROM res_city_div
                    WHERE city_id = %s AND hierarchical_id LIKE %s AND id != %s
                """,
                    (prefix, rec.city_id.id, prefix + "%", rec.id),
                )
                max_existing = self.env.cr.fetchone()[0] or 0

                rec.hierarchical_id = f"{prefix}{max_existing + 1:03d}"

        return res
