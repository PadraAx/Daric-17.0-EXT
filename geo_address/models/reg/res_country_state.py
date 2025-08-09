from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.mail.models.mail_thread import MailThread
from odoo.addons.mail.models.mail_activity_mixin import MailActivityMixin
from contextlib import contextmanager
import logging
import re

_logger = logging.getLogger(__name__)


class CountryState(models.Model, MailThread, MailActivityMixin):
    # ==========================================================================
    # Model Metadata
    # ==========================================================================
    _inherit = "res.country.state"
    _name = "res.country.state"
    _description = "Extended Country State"
    _order = "country_id, name"
    # ==========================================================================
    # Fields Definition
    # ==========================================================================
    # ============================================
    # Descriptive Fields
    # ============================================
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
    capital_id = fields.Many2one(
        "res.city",
        string="State Capital",
        domain="[('state_id', '=', id), ('country_id', '=', country_id)]",  # Changed to strict matching
        help="The capital city of this state",
        ondelete="set null",
        tracking=True,
    )
    capital_name = fields.Char(
        string="Capital Name", related="capital_id.name", store=True, readonly=True
    )
    county_ids = fields.One2many("res.county", "state_id", string="Counties")
    # ============================================
    # Identification Fields
    # ============================================
    # system_id = fields.Char(
    #     string="System ID",
    #     required=True,
    #     index=True,
    #     readonly=True,
    #     tracking=True,
    # )
    hierarchical_id = fields.Char(
        string="Hierarchical ID",
        compute="_compute_hierarchical_id",
        store=True,
        readonly=True,
    )
    iso_code = fields.Char(
        string="ISO Code",
        tracking=True,
        readonly=True,
        store=True,
        help="Enter ISO Code",
    )
    address_ids = fields.One2many("res.address", "state_id", string="Addresses")
    partner_count = fields.Integer(
        string="Partner Count",
        compute="_compute_partner_count",
        store=True,
        help="Total partners in this country",
    )
    # ==========================================================================
    # SQL Constraints & Indexes
    # ==========================================================================
    _sql_constraints = [
        # (
        #     "system_id_uniq",
        #     "UNIQUE(system_id)",
        #     "The system identifier must be unique.",
        # ),
        # (
        #     "system_id_format_check",
        #     "CHECK (char_length(system_id) = 10 AND system_id ~ '^[0-9]+$')",
        #     "System ID must be exactly 10 digits long and contain only numbers.",
        # ),
        (
            "iso_code_uniq",
            "UNIQUE(iso_code)",
            "The ISO code must be unique.",
        ),
        (
            "capital_in_state_check",
            "CHECK (capital_id IS NULL OR capital_id.state_id = id)",
            "The capital city must belong to this state!",
        ),
        (
            "capital_country_consistency_check",
            "CHECK (capital_id IS NULL OR capital_id.country_id = country_id)",
            "The capital city must belong to the same country as the state!",
        ),
        (
            "hierarchical_id_unique",
            "UNIQUE(hierarchical_id)",
            "Hierarchical ID must be unique.",
        ),
    ]

    # ==========================================================================
    # Methods
    # ==========================================================================
    # ============================================
    # External Relational Fields Related Methods
    # ============================================
    @contextmanager
    def capital_change_context(self):
        """Context manager for safe capital city changes"""
        try:
            yield
            self._ensure_capital_consistency()
        except Exception as e:
            _logger.error("Failed to update capital: %s", e)
            raise

    # In res.country.state model:

    @api.onchange("capital_id")
    def _onchange_capital_id(self):
        """Sync capital_id changes with city flags"""
        if not self.capital_id:
            # Clear all state capital flags if unsetting capital
            self.env["res.city"].search(
                [("state_id", "=", self.id), ("is_state_capital", "=", True)]
            ).write({"is_state_capital": False})
        else:
            # Ensure the city is marked as capital
            if not self.capital_id.is_state_capital:
                self.capital_id.write(
                    {
                        "is_state_capital": True,
                        "state_id": self.id,
                        "country_id": self.country_id.id,
                    }
                )
            # Clear any other cities marked as capital
            self.env["res.city"].search(
                [
                    ("state_id", "=", self.id),
                    ("is_state_capital", "=", True),
                    ("id", "!=", self.capital_id.id),
                ]
            ).write({"is_state_capital": False})

    def action_check_consistency(self):
        """Button action to verify and repair data consistency"""
        inconsistent_records = self.search(
            [("capital_id.is_state_capital", "=", False)]
        )
        inconsistent_records._ensure_capital_consistency()

        return {
            "effect": {
                "fadeout": "slow",
                "message": _("Consistency check completed. Fixed %s states")
                % len(inconsistent_records),
                "type": "rainbow_man",
            }
        }

    def _ensure_capital_consistency(self):
        """Ensure capital cities are properly marked as state capitals"""
        for state in self:
            if state.capital_id and not state.capital_id.is_state_capital:
                state.capital_id.write(
                    {
                        "is_state_capital": True,
                        "state_id": state.id,
                        "country_id": state.country_id.id,
                    }
                )

    def open_capital_city(self):
        """Open the capital city form view"""
        self.ensure_one()
        if not self.capital_id:
            raise ValidationError(_("This state has no capital city assigned"))
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.city",
            "view_mode": "form",
            "res_id": self.capital_id.id,
            "target": "current",
            "context": {
                "create": False,
                "edit": True,
                "form_view_initial_mode": "edit",
            },
        }

    @api.depends("address_ids.partner_count")
    def _compute_partner_count(self):
        for state in self:
            state.partner_count = sum(state.address_ids.mapped("partner_count"))

    # ============================================
    # Identification Fields Related Methods
    # ============================================
    # @api.constrains("system_id")
    # def _check_system_id_format(self):
    #     for record in self:
    #         if not (
    #             record.system_id
    #             and record.system_id.isdigit()
    #             and len(record.system_id) == 10
    #         ):
    #             raise ValidationError(
    #                 "System ID must be exactly 10 digits and numeric."
    #             )

    # @api.depends("country_id.code", "system_id")
    # def _compute_hierarchical_id(self):
    #     for record in self:
    #         if record.country_id.code and record.system_id:
    #             record.hierarchical_id = f"{record.country_id.code}-{record.system_id}"
    #         else:
    #             record.hierarchical_id = False

    @api.depends("country_id")
    def _compute_hierarchical_id(self):
        for record in self:
            if not record.country_id:
                record.hierarchical_id = False
                continue

            # Get all other records for the same country with hierarchical_id already assigned
            existing_ids = self.search(
                [
                    ("country_id", "=", record.country_id.id),
                    ("id", "!=", record.id),
                    ("hierarchical_id", "!=", False),
                ]
            )

            if len(existing_ids) >= 99:
                _logger.warning(
                    f"Cannot assign Hierarchical ID: all 99 positions are already used for country {record.country_id.code or record.country_id.name or 'UNKNOWN'}."
                )

                record.hierarchical_id = False
                continue

            # Find the next available position (from 1 to 99) that’s not used
            used_positions = {
                int(r.hierarchical_id[2:4])
                for r in existing_ids
                if r.hierarchical_id
                and r.hierarchical_id.startswith(record.country_id.code)
                and r.hierarchical_id[2:4].isdigit()
            }

            available_position = next(
                (i for i in range(1, 100) if i not in used_positions), None
            )

            if available_position is None:
                record.hierarchical_id = False
                continue

            # Compose hierarchical ID: CCNN + padding to 12 chars
            position_str = str(available_position).zfill(2)
            base_id = f"{record.country_id.code}{position_str}"
            record.hierarchical_id = base_id.ljust(12, "0")

    # ============================================
    # CRUD Methods
    # ============================================
    def write(self, vals):
        """Handle capital city changes during write operations"""
        if "capital_id" in vals:
            # Clear is_state_capital from old capitals
            if vals["capital_id"] is False:  # When unsetting capital
                self.env["res.city"].search(
                    [("state_id", "in", self.ids), ("is_state_capital", "=", True)]
                ).write({"is_state_capital": False})
            else:
                # Clear flags from cities that are no longer capitals
                old_capitals = self.env["res.city"].search(
                    [
                        ("state_id", "in", self.ids),
                        ("is_state_capital", "=", True),
                        (
                            "id",
                            "not in",
                            (
                                vals["capital_id"]
                                if isinstance(vals["capital_id"], (list, tuple))
                                else [vals["capital_id"]]
                            ),
                        ),
                    ]
                )
                old_capitals.write({"is_state_capital": False})

                with self.capital_change_context():
                    # Your existing write logic
                    return super().write(vals)
                # Set flag on new capital
                new_capital = self.env["res.city"].browse(vals["capital_id"])
                if not new_capital.is_state_capital:
                    new_capital.write(
                        {
                            "is_state_capital": True,
                            "state_id": self.id,  # Ensure proper state assignment
                            "country_id": self.country_id.id,  # Ensure proper country assignment
                        }
                    )

        return super().write(vals)
