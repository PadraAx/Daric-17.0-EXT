from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    address_hierarchical_id = fields.Char(
        related="address_id.hierarchical_id",
        string="Address Hierarchical ID",
        readonly=True,
        store=True,
    )
    address_address_text = fields.Text(
        related="address_id.address_text",
        string="Address Text",
        readonly=True,
        store=True,
    )
    address_address_type = fields.Selection(
        related="address_id.address_type",
        string="Geo Address Type",  # Updated label
        readonly=True,
        store=True,
    )
    address_id = fields.Many2one(
        "res.address", string="Address Reference", ondelete="set null", tracking=True
    )
    address_country_id = fields.Many2one(
        related="address_id.country_id",
        string="Geo Country",  # Updated label
        store=True,
        readonly=True,
    )

    address_state_id = fields.Many2one(
        related="address_id.state_id",
        string="Geo State",  # Updated label
        store=True,
        readonly=True,
    )

    address_county_id = fields.Many2one(
        related="address_id.county_id",
        store=True,
        readonly=True,
    )

    address_postal_code = fields.Char(
        related="address_id.postal_code",
        store=True,
        readonly=True,
    )
    has_address_id = fields.Boolean(compute="_compute_has_address_id", store=True)

    @api.depends("address_id")
    def _compute_has_address_id(self):
        for rec in self:
            rec.has_address_id = bool(rec.address_id)

    @api.onchange("address_id")
    def _onchange_address_id(self):
        if self.address_id:
            self.update(
                {
                    "country_id": self.address_id.country_id.id,
                    "state_id": self.address_id.state_id.id,
                    "city_id": self.address_id.city_id.id,
                    "zip": self.address_id.postal_code or "",
                    "street": self.address_id.address_text or "",
                    "street2": False,
                    "street_name": False,
                    "street_number": False,
                    "street_number2": False,
                }
            )

    def name_get(self):
        result = []
        for partner in self:
            name = partner.name or ""
            if partner.address_id:
                addr = partner.address_id.address_text or ""
                name = f"{name} ({addr})" if addr else name
            result.append((partner.id, name))
        return result
