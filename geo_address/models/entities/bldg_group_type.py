# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class BldgGroupType(models.Model):
    _name = "bldg.group.type"
    _description = "Building Group Type"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"
    _sql_constraints = [
        ("code_uniq", "UNIQUE(code)", _("The code must be unique!")),
    ]

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------
    code = fields.Char(
        string="Reference Code",
        required=True,
        size=4,
        help="4-character code: 2 uppercase letters (A-Z) + 2 digits (0-9). Example: RC01",
        index=True,
    )

    name = fields.Char(
        string="Type Name",
        required=True,
        translate=True,
        help="The display name of the building group type (e.g., 'Residential Complex', 'Commercial Tower')",
    )

    description = fields.Text(
        string="Detailed Description",
        translate=True,
        help="Full description of what this building type represents",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, this type will be hidden in views",
    )

    sequence = fields.Integer(
        string="Priority",
        help="Determines display order in dropdowns (lower numbers show first)",
        default=10,
    )

    color = fields.Integer(
        string="Color",
        help="Color for visual distinction in kanban and calendar views",
    )

    bldg_group_ids = fields.One2many(
        comodel_name="bldg.group",
        inverse_name="bldg_group_type_id",
        string="Building Groups",
        help="All building groups classified under this type",
    )

    bldg_group_count = fields.Integer(
        compute="_compute_bldg_group_count",
        string="Building Groups Count",
        store=False,
        help="Technical field to show count of related building groups",
    )

    # ----------------------------------------------------------
    # Constraints and Validations
    # ----------------------------------------------------------
    @api.constrains("code")
    def _check_code_format(self):
        """Enforce AA00 format where A=letter, 0=digit"""
        for record in self:
            if not record.code:
                continue
            if not re.match(r"^[A-Z]{2}\d{2}$", record.code):
                raise ValidationError(
                    _(
                        "Invalid code format! Must be exactly 4 characters: "
                        "2 uppercase letters followed by 2 digits. Example: AB12"
                    )
                )

    # ----------------------------------------------------------
    # Onchange Methods
    # ----------------------------------------------------------
    @api.onchange("code")
    def _onchange_code_autoformat(self):
        """Auto-format code as user types"""
        if self.code:
            # Remove all non-alphanumeric characters
            clean_code = re.sub(r"[^A-Za-z0-9]", "", self.code)
            # Convert to uppercase
            clean_code = clean_code.upper()

            # Auto-format partial entries
            if len(clean_code) >= 2:
                letters = clean_code[:2]
                numbers = clean_code[2:4] if len(clean_code) > 2 else "00"
                self.code = f"{letters}{numbers}".ljust(4, "0")[:4]
            else:
                self.code = clean_code.ljust(4, "0")[:4]

    # ----------------------------------------------------------
    # CRUD Methods
    # ----------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure code formatting"""
        for vals in vals_list:
            if "code" in vals and vals["code"]:
                vals["code"] = self._format_code(vals["code"])
        return super().create(vals_list)

    def write(self, vals):
        """Override write to ensure code formatting"""
        if "code" in vals and vals["code"]:
            vals["code"] = self._format_code(vals["code"])
        return super().write(vals)

    # ----------------------------------------------------------
    # Business Logic
    # ----------------------------------------------------------
    def _format_code(self, raw_code):
        """Internal: Format code to AA00 standard"""
        if not raw_code:
            return raw_code

        # Clean input
        clean_code = re.sub(r"[^A-Za-z0-9]", "", str(raw_code)).upper()

        # Ensure proper format
        letters = clean_code[:2] if len(clean_code) >= 2 else "XX"
        digits = clean_code[2:4] if len(clean_code) >= 4 else "00"

        # Validate letters and digits
        letters = "".join([c if c.isalpha() else "X" for c in letters])
        digits = "".join([d if d.isdigit() else "0" for d in digits])

        return f"{letters[:2]}{digits[:2]}"

    def _compute_bldg_group_count(self):
        """Calculate number of related building groups"""
        group_data = self.env["bldg.group"].read_group(
            [("bldg_group_type_id", "in", self.ids)],
            ["bldg_group_type_id"],
            ["bldg_group_type_id"],
        )
        mapped_data = {
            item["bldg_group_type_id"][0]: item["bldg_group_type_id_count"]
            for item in group_data
        }
        for record in self:
            record.bldg_group_count = mapped_data.get(record.id, 0)

    # ----------------------------------------------------------
    # UI Actions
    # ----------------------------------------------------------
    def action_view_bldg_groups(self):
        """Smart button action to view related building groups"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Building Groups of Type: %s") % self.name,
            "res_model": "bldg.group",
            "view_mode": "tree,form",
            "domain": [("bldg_group_type_id", "=", self.id)],
            "context": {
                "default_bldg_group_type_id": self.id,
                "search_default_bldg_group_type_id": self.id,
            },
            "target": "current",
        }
