# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
from odoo.tools import image_process
import logging

_logger = logging.getLogger(__name__)


class RuralDistrictDivision(models.Model):
    _name = "res.rural.dist.div"
    _description = "Rural District Division"
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
        help="Detailed description of the rural district division",
    )
    # ============================================
    # External Relational Fields
    # ============================================
    rural_dist_id = fields.Many2one(
        "res.rural.dist", required=True, ondelete="cascade", index=True, tracking=True
    )
    county_id = fields.Many2one(
        "res.county", related="rural_dist_id.county_id", store=True, string="County"
    )
    state_id = fields.Many2one(
        "res.country.state",
        related="rural_dist_id.county_id.state_id",
        store=True,
        string="State",
    )
    country_id = fields.Many2one(
        "res.country",
        related="rural_dist_id.county_id.state_id.country_id",
        store=True,
        string="Country",
    )
    bldg_ids = fields.One2many(
        "bldg.building",
        "rural_dist_div_id",
        string="Buildings in This Rural Division",
    )
    # ============================================
    # Internal Relational Fields
    # ============================================
    full_path = fields.Char(
        compute="_compute_full_path", store=True, recursive=True, string="Full Path"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    parent_id = fields.Many2one(
        "res.rural.dist.div",
        ondelete="cascade",
        domain="[('rural_dist_id', '=', rural_dist_id)]",
        index=True,
        tracking=True,
    )
    generation = fields.Integer(
        string="Generation", compute="_compute_generation", store=True
    )
    sibling_count = fields.Integer(
        string="Siblings in Same Generation", compute="_compute_sibling_count"
    )
    child_ids = fields.One2many(
        "res.rural.dist.div", "parent_id", string="Child Divisions"
    )
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
        "Thumbnail", related="profile_image", max_width=256, max_height=256, store=True
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
        help="Format: [CountryCode]-[DistSystemID]-[DivisionID]",
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
        ),
        (
            "unique_division_hierarchy",
            "unique(country_id, state_id, county_id, rural_dist_id, parent_id)",
            "Division name must be unique within the full geographic hierarchy!",
        ),
    ]

    _index = [
        ("parent_path", "btree"),
        ("rural_dist_id", "btree"),
        ("generation", "btree"),
        ("hierarchical_id", "btree"),
        ("parent_id", "btree"),
        (("rural_dist_id", "parent_id"), "btree"),
    ]

    # ==========================================================================
    # Methods
    # ==========================================================================
    # ============================================
    # Descriptive Fields Related Methods
    # ============================================
    def name_get(self):
        result = []
        for rec in self:
            name = rec.full_path or f"{rec.rural_dist_id.name or ''} / {rec.name}"
            result.append((rec.id, name))
        return result

    # ============================================
    # Internal Relational Fields Related Methods
    # ============================================
    def _get_all_children(self):
        return self.search([("parent_path", "=like", f"{self.parent_path}%")])

    @api.depends("parent_id")
    def _compute_generation(self):
        for rec in self:
            if rec.parent_id:
                rec.generation = rec.parent_id.generation + 1
            else:
                rec.generation = 1

    @api.depends("parent_id", "rural_dist_id")
    def _compute_sibling_count(self):
        for rec in self:
            if not isinstance(rec.id, int):
                rec.sibling_count = 0
                continue
            domain = [
                ("rural_dist_id", "=", rec.rural_dist_id.id),
                ("parent_id", "=", rec.parent_id.id if rec.parent_id else False),
                ("id", "!=", rec.id),
            ]
            rec.sibling_count = self.search_count(domain) + 1

    @api.depends("name", "parent_id.full_path", "rural_dist_id.name")
    def _compute_full_path(self):
        for rec in self:
            if rec.parent_id:
                rec.full_path = f"{rec.parent_id.full_path} / {rec.name}"
            else:
                rec.full_path = f"{rec.rural_dist_id.name or ''} / {rec.name}"

    # ============================================
    # Validation Methods
    # ============================================
    # @api.constrains(
    #     "name", "country_id", "state_id", "county_id", "rural_dist_id", "parent_id"
    # )
    # def _check_unique_in_hierarchy(self):
    #     for rec in self:
    #         domain = [
    #             ("name", "=", rec.name),
    #             ("country_id", "=", rec.country_id.id),
    #             ("state_id", "=", rec.state_id.id),
    #             ("county_id", "=", rec.county_id.id),
    #             ("rural_dist_id", "=", rec.rural_dist_id.id),
    #             ("parent_id", "=", rec.parent_id.id if rec.parent_id else False),
    #             ("id", "!=", rec.id),
    #         ]
    #         if self.search_count(domain):
    #             raise ValidationError(
    #                 _("Division '%s' already exists in this location hierarchy!")
    #                 % rec.name
    #             )

    # ============================================
    # Media Fields Related Methods
    # ============================================
    @api.depends("attachment_ids")
    def _compute_gallery_count(self):
        for rec in self:
            rec.gallery_count = len(rec.attachment_ids)

    def add_to_gallery(self, media_type, **kwargs):
        self.ensure_one()
        file_data = kwargs.get("file_data")
        name = kwargs.get("name", "Untitled Media")
        mimetype = kwargs.get("mimetype")
        if not mimetype:
            mimetype = {
                "image": "image/jpeg",
                "video": "video/mp4",
                "document": "application/pdf",
            }.get(media_type, "application/octet-stream")
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

    @api.model_create_multi
    def create(self, vals_list):
        # Group records by rural_dist_id (for hierarchical_id assignment)
        grouped_by_dist = {}
        for vals in vals_list:
            rural_dist_id = vals.get("rural_dist_id")
            if rural_dist_id:
                grouped_by_dist.setdefault(rural_dist_id, []).append(vals)
            else:
                vals["hierarchical_id"] = False

        # Assign hierarchical_id (no uniqueness check on 'name')
        for rural_dist_id, records in grouped_by_dist.items():
            dist = self.env["res.rural.dist"].browse(rural_dist_id)
            dist_hier_id = dist.hierarchical_id

            # Skip hierarchical_id assignment if invalid
            if not dist_hier_id or not dist_hier_id.endswith("000"):
                for vals in records:
                    vals["hierarchical_id"] = False
                continue

            # Assign hierarchical_id (e.g., "IR010010010001", "IR010010010002", ...)
            prefix = dist_hier_id[:-3]  # Remove last 3 digits (e.g., "000")
            existing = self.search([("rural_dist_id", "=", rural_dist_id)], order="id")

            # Update existing records (if needed)
            for idx, div in enumerate(existing, start=1):
                div.hierarchical_id = f"{prefix}{idx:03d}"

            # Assign new hierarchical_ids
            base_index = len(existing)
            for i, vals in enumerate(records, start=1):
                vals["hierarchical_id"] = f"{prefix}{(base_index + i):03d}"

        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if "rural_dist_id" in vals:
            for rec in self:
                if (
                    not rec.rural_dist_id
                    or not rec.rural_dist_id.hierarchical_id.endswith("000")
                ):
                    rec.hierarchical_id = False
                    continue

                prefix = rec.rural_dist_id.hierarchical_id[:-3]
                self.env.cr.execute(
                    """
                    SELECT MAX(CAST(SUBSTRING(hierarchical_id FROM LENGTH(%s)+1 FOR 3) AS INTEGER))
                    FROM res_rural_dist_div
                    WHERE rural_dist_id = %s AND hierarchical_id LIKE %s AND id != %s
                """,
                    (prefix, rec.rural_dist_id.id, prefix + "%", rec.id),
                )
                max_existing = self.env.cr.fetchone()[0] or 0
                rec.hierarchical_id = f"{prefix}{max_existing + 1:03d}"
        return res
