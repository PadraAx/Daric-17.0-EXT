# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class RuralDistrict(models.Model):
    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _name = "res.rural.dist"
    _description = "Rural District"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"
    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # Descriptive Fields
    # ============================================
    name = fields.Char(
        string="Rural District Name", required=True, translate=True, tracking=True
    )
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=True,
        prefetch=False,
        help="Detailed description of the rural district",
    )
    # ============================================
    # Relational Fields
    # ============================================
    country_id = fields.Many2one("res.country", string="Country", required=True)
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        domain="[('country_id', '=', country_id)]",
        required=True,
    )
    county_id = fields.Many2one(
        "res.county",
        string="County",
        domain="[('state_id', '=', state_id)]",
        required=True,
    )
    rural_dist_div_ids = fields.One2many(
        "res.rural.dist.div", "rural_dist_id", string="Rural District Divisions"
    )
    address_ids = fields.One2many("res.address", "rural_dist_id", string="Addresses")

    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        help="Total partners in this city (including city divisions)",
    )

    # ============================================
    # Identification Fields
    # ============================================
    hrchy_id = fields.Many2one(
        "hrchy.id",
        string="Hierarchy Reference",
        compute="_compute_hrchy_id",
        store=True,
        index=True,
    )

    def _compute_hrchy_id(self):
        for country in self:
            hrchy_record = self.env["hrchy.id"].search(
                [
                    ("country_id", "=", country.id),
                    ("state_id", "=", False),
                    ("county_id", "=", False),
                    ("city_id", "=", False),
                    ("rural_id", "=", False),
                ],
                limit=1,
            )
            country.hrchy_id = hrchy_record

    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        index=True,
        readonly=True,
        copy=False,
        help="Format: [CountryCode]-[State(2)County(2)Type(2)Seq(2)Reserved(3)]",
    )
    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = []

    # ==========================================================================
    # Methods
    # ==========================================================================
    # ============================================
    # Relational Fields Related Methods
    # ============================================
    @api.depends("address_ids.partner_count")
    def _compute_partner_count(self):
        for rural_dist in self:
            rural_dist.partner_count = sum(
                rural_dist.address_ids.mapped("partner_count")
            )

    @api.depends("county_id")
    def _compute_state(self):
        """Auto-set state based on selected county"""
        for district in self:
            if district.county_id and district.county_id.state_id:
                district.state_id = district.county_id.state_id

    @api.onchange("country_id")
    def _onchange_country_id(self):
        self.state_id = False
        return {"domain": {"state_id": [("country_id", "=", self.country_id.id)]}}

    @api.onchange("state_id")
    def _onchange_state_id(self):
        self.county_id = False
        return {"domain": {"county_id": [("state_id", "=", self.state_id.id)]}}

    # ============================================
    # CRUD Methods
    # ============================================
    # @api.model_create_multi
    # def create(self, vals_list):
    #     # FIRST: Resolve any XML ID references in foreign keys (for CSV import)
    #     for vals in vals_list:
    #         for field in ("country_id", "state_id", "county_id"):
    #             ref = vals.get(field)
    #             if isinstance(ref, str) and "." in ref:
    #                 try:
    #                     vals[field] = self.env.ref(ref).id
    #                 except ValueError:
    #                     raise ValidationError(
    #                         _("Invalid XML ID for %s: %s") % (field, ref)
    #                     )

    #     # Call super with resolved vals
    #     districts = super().create(vals_list)

    #     # Group created districts by county_id
    #     county_groups = {}
    #     for district in districts:
    #         county_groups.setdefault(district.county_id.id, []).append(district)

    #     # Assign hierarchical IDs
    #     for county_id, district_list in county_groups.items():
    #         county = district_list[0].county_id
    #         if not (county and county.hierarchical_id and county.country_id):
    #             continue

    #         # Lock the county row to prevent race conditions
    #         self.env.cr.execute(
    #             "SELECT 1 FROM res_county WHERE id = %s FOR UPDATE", (county.id,)
    #         )

    #         parts = county.hierarchical_id.split("-")
    #         if len(parts) != 2 or len(parts[1]) != 10:
    #             raise ValidationError(_("Invalid county hierarchical ID format."))

    #         county_code = parts[1][:4]
    #         country_code = county.country_id.code

    #         self.env.cr.execute(
    #             """
    #             SELECT MAX(CAST(SUBSTRING(hierarchical_id, 8, 2) AS INTEGER))
    #             FROM res_rural_dist
    #             WHERE county_id = %s AND hierarchical_id LIKE %s
    #             """,
    #             (county.id, f"{country_code}-{county_code}2%"),
    #         )
    #         max_seq = self.env.cr.fetchone()[0] or 0

    #         update_vals = []
    #         for idx, district in enumerate(district_list, start=1):
    #             seq = max_seq + idx
    #             if seq > 99:
    #                 raise ValidationError(
    #                     _("Maximum rural districts (99) reached for county: %s")
    #                     % county.name
    #                 )
    #             new_id = f"{country_code}-{county_code}2{seq:02d}000"
    #             update_vals.append((new_id, district.id))

    #         if update_vals:
    #             self.env.cr.executemany(
    #                 "UPDATE res_rural_dist SET hierarchical_id = %s WHERE id = %s",
    #                 update_vals,
    #             )

    #     return districts
    @api.model_create_multi
    def create(self, vals_list):
        # 1. Resolve XML-ID references
        for vals in vals_list:
            for field in ("country_id", "state_id", "county_id"):
                ref = vals.get(field)
                if isinstance(ref, str) and "." in ref:
                    try:
                        vals[field] = self.env.ref(ref).id
                    except ValueError:
                        raise ValidationError(
                            _("Invalid XML ID for %s: %s") % (field, ref)
                        )

        # 2. Create the records
        districts = super().create(vals_list)

        # 3. Assign hierarchical IDs
        county_groups = {}
        for district in districts:
            county_groups.setdefault(district.county_id.id, []).append(district)

        for county_id, district_list in county_groups.items():
            county = district_list[0].county_id
            if not (county and county.hierarchical_id and county.country_id):
                continue

            cid = county.hierarchical_id
            if len(cid) != 12 or not cid.startswith(county.country_id.code):
                raise ValidationError(_("Invalid county hierarchical ID format."))

            county_prefix = cid[:6]  # CCSScc

            self.env.cr.execute(
                """
                SELECT MAX(CAST(SUBSTRING(hierarchical_id, 7, 2) AS INTEGER))
                FROM res_rural_dist
                WHERE county_id = %s
                AND hierarchical_id LIKE %s
                """,
                (county.id, f"{county_prefix}2%"),
            )
            max_seq = self.env.cr.fetchone()[0] or 0

            update_vals = []
            for idx, district in enumerate(district_list, start=1):
                seq = max_seq + idx
                if seq > 99:
                    raise ValidationError(
                        _("Maximum rural districts (99) reached for county: %s")
                        % county.name
                    )
                new_id = f"{county_prefix}2{seq:02d}000"
                update_vals.append((new_id, district.id))

            if update_vals:
                self.env.cr.executemany(
                    "UPDATE res_rural_dist SET hierarchical_id = %s WHERE id = %s",
                    update_vals,
                )

        return districts

    def write(self, vals):
        if "county_id" in vals:
            # Split changed vs unchanged records
            county_changes = self.filtered(
                lambda d: d.county_id.id != vals["county_id"]
            )
            unchanged = self - county_changes

            if county_changes:
                new_county = self.env["res.county"].browse(vals["county_id"])
                if not new_county.hierarchical_id:
                    raise ValidationError(_("Selected county has no hierarchical ID."))

                self.env.cr.execute(
                    "SELECT 1 FROM res_county WHERE id = %s FOR UPDATE",
                    (new_county.id,),
                )
                parts = new_county.hierarchical_id.split("-")
                if len(parts) != 2 or len(parts[1]) != 10:
                    raise ValidationError(_("Invalid county hierarchical ID format."))

                county_code = parts[1][:4]
                country_code = new_county.country_id.code

                self.env.cr.execute(
                    """
                        SELECT MAX(CAST(SUBSTRING(hierarchical_id, 8, 2) AS INTEGER))
                        FROM res_rural_dist
                        WHERE county_id = %s AND hierarchical_id LIKE %s
                    """,
                    (new_county.id, f"{country_code}-{county_code}2%"),
                )
                max_seq = self.env.cr.fetchone()[0] or 0

                update_vals = []
                for idx, district in enumerate(county_changes, start=1):
                    seq = max_seq + idx
                    if seq > 99:
                        raise ValidationError(
                            _("Maximum rural districts (99) reached for county: %s")
                            % new_county.name
                        )
                    new_id = f"{country_code}-{county_code}2{seq:02d}000"
                    update_vals.append((new_id, district.id))

                if update_vals:
                    self.env.cr.executemany(
                        """UPDATE res_rural_dist 
                            SET hierarchical_id = %s, county_id = %s 
                            WHERE id = %s""",
                        [(hid, new_county.id, did) for hid, did in update_vals],
                    )

                # Apply remaining vals to unchanged
                remaining_vals = {k: v for k, v in vals.items() if k != "county_id"}
                if remaining_vals:
                    unchanged.write(remaining_vals)

                return True

        return super().write(vals)
