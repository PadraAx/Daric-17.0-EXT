# -*- coding: utf-8 -*-

import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError


def apply_notification(method):
    def inner(obj):
        method(obj)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "danger" if obj.state == "deraft" else "success",
                "title": _("Successfully!"),
                "message": _(f"Status changed into {obj.state}"),
                "next": {"type": "ir.actions.act_window_close"},
            },
        }

    inner.__wrapped__ = method
    return inner


class AssetComponent(models.Model):
    _name = "asset.component"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True
    _order = "asset_number desc, create_date desc"
    # _rec_name = 'asset_number'

    def _default_picking_type_id(self):
        picking_types = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                ("company_id", "=", self.env.company.id),
            ]
        )
        return picking_types[:1].id

    def get_location_domain(self):
        domain = [("replenish_location", "=", True)]
        if not self.env.user.has_group("dhs_asset_mgt.group_it_asset_admin"):
            domain.append(("user_ids", "in", self.env.user.id))
        return domain

    def _get_has_access(self):
        for record in self:
            record.has_access = True

    def _compute_display_name(self):
        for record in self:
            data = record.create_date.strftime("%Y-%m-%d")
            record.display_name = f"{record.using_user.name}-{data}"

    @api.depends("item_product", "product_id")
    def _compute_lot_info(self):
        for record in self:
            if record.item_product and record.product_id:
                move_line = record.item_product.move_line_ids.filtered(
                    lambda item: item.product_id.id == record.product_id.id
                )
                if len(move_line) > 1:
                    move_line = move_line[0]
                record.price = move_line.price
                record.lot_id = move_line.lot_id.id

    @api.depends("product_id", "location_id")
    def get_product_qty_available(self):
        for record in self:
            qty = 0
            if record.product_id and record.location_id:
                qty = self.env["stock.quant"]._get_available_quantity(
                    record.product_id, record.location_id
                )
            record.product_qty_available = qty

    @api.depends("history_id")
    def get_last_action(self):
        for record in self:
            history_items = record.history_id.sorted("date", reverse=True)
            last_history = history_items[0] if history_items else False
            record.last_action = last_history.action if last_history else "draft"
            record.last_action_date = (
                last_history.date
                if last_history
                else record.date_issue or record.create_date
            )

    # ---------------------------------------------------
    #  CONSTRAINS
    # ---------------------------------------------------

    @api.constrains("using_user", "state")
    def check_duplicate_user(self):
        params = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("dhs_asset_mgt.admins_notification_ids")
        )
        admins = (
            self.env["res.partner"].search([("id", "in", json.loads(params))])
            if params
            else []
        )
        for record in self:
            if record.state == "running" and admins:
                on_hand = self.sudo().search(
                    [
                        ("using_user", "=", record.using_user.id),
                        ("product_id", "=", record.product_id.id),
                        ("state", "=", "running"),
                    ]
                )
                if len(on_hand) > 1:
                    for userAdmin in admins:
                        mail_context = {
                            "admin": userAdmin,
                            "user": record.using_user,
                            "record": record,
                        }
                        asset_template = self.env.ref(
                            "dhs_asset_mgt.mail_template_asset_component",
                            raise_if_not_found=False,
                        )
                        asset_template and asset_template.sudo().with_context(
                            **mail_context
                        ).send_mail(
                            record.id,
                            force_send=True,
                            email_layout_xmlid="mail.mail_notification_light",
                        )

    @api.constrains("product_id", "location_id", "state")
    def check_product_qty_available(self):
        for record in self:
            if record.state == "draft" and record.product_qty_available < 1:
                raise UserError(_("The product quantity available is not enough."))

    # ---------------------------------------------------
    #  FIELDS
    # ---------------------------------------------------

    asset_number = fields.Char(string="Component Number")
    date_issue = fields.Datetime(string="Date Issue")
    product_id = fields.Many2one(
        "product.product", "Product", required=True, tracking=True
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("running", "Running"),
            ("returned", "Returned"),
            ("retired", "Retired"),
        ],
        default="draft",
        tracking=True,
        index=True,
    )
    material_request_id = fields.Many2one(
        "material.request", "Material Request", tracking=True
    )
    item_product = fields.Many2one(
        "stock.picking", "Operation Reference", tracking=True, readonly=True
    )
    currency_id = fields.Many2one(related="product_id.currency_id")
    price = fields.Monetary(
        "Price",
        copy=False,
        store=True,
        compute="_compute_lot_info",
        readonly=True,
        sudo=True,
    )
    lot_id = fields.Many2one(
        "stock.lot",
        "Lot/Serial Number",
        store=True,
        readonly=True,
        compute="_compute_lot_info",
        sudo=True,
    )

    using_user = fields.Many2one(
        "res.partner",
        string="Asignee",
        tracking=True,
        store=True,
        check_company=True,
        required=False,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        readonly=True,
        required=True,
        default=lambda s: s.env.company.id,
        index=True,
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Operation Type",
        required=True,
        index=True,
        default=_default_picking_type_id,
    )
    location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        domain=get_location_domain,
        store=True,
        check_company=True,
        required=True,
    )
    os_type = fields.Char("OS Type", tracking=True)
    ip_address = fields.Char(string="IP Address", tracking=True)
    license = fields.Char(string="License", tracking=True)
    component_serial_number = fields.Char("Serial Number", tracking=True)
    component_warranty = fields.Char("Warranty (In Months)", tracking=True)
    component_buydate = fields.Date("Buy Date", tracking=True)
    component_warranty_end_date = fields.Date("Warranty End Date", tracking=True)
    component_note = fields.Text()
    asser_kind = fields.Selection(
        [("physical", "Physical"), ("virtual", "Virtual")],
        default="physical",
        string="Asset Kind",
        tracking=True,
    )

    has_access = fields.Boolean(compute="_get_has_access")
    history_id = fields.One2many("asset.history", "asset_id", "Hisotry", tracking=True)
    product_qty_available = fields.Float(
        "On Hand Quantity", compute="get_product_qty_available", readonly=True
    )
    last_action = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("running", "Running"),
            ("returned", "Returned"),
            ("reassigment", "Reassigment"),
            ("retired", "Retired"),
        ],
        string="Last Action",
        compute="get_last_action",
        store=True,
    )
    last_action_date = fields.Datetime(
        "Last Action Date", compute="get_last_action", store=True
    )

    _sql_constraints = [
        (
            "unique_component_serial_number",
            "unique(component_serial_number) WHERE (component_serial_number IS NOT NULL)",
            "component Serial Number must be unique!",
        ),
    ]

    # ---------------------------------------------------
    #  BUTTONS
    # ---------------------------------------------------

    @apply_notification
    def to_draft(self):
        self.write({"state": "draft"})
        # self.send_email_notification('knowledge_ext.mail_template_knowledge_draft')

    @apply_notification
    def to_running(self):
        if not self.using_user:
            raise UserError(_("َAsset should be assaing before running"))
        if self.product_qty_available < 1:
            raise UserError(_("The product quantity available is not enough."))
        fields = [
            "move_type",
            "priority",
            "scheduled_date",
            "date",
            "picking_type_id",
            "user_id",
            "is_locked",
        ]
        stock_packing_values = (
            self.env["stock.picking"]
            .sudo()
            .with_context(
                {
                    "restricted_picking_type_code": "outgoing",
                }
            )
            .default_get(fields)
        )
        picking_type_id = (
            self.sudo()
            .env["stock.picking.type"]
            .search(
                [
                    ("code", "=", "outgoing"),
                    ("company_id", "=", self.env.user.company_id.id),
                    ("warehouse_id", "=", self.location_id.warehouse_id.id),
                ],
                limit=1,
            )
        )
        customer_loc, supplier_loc = (
            self.location_id.warehouse_id._get_partner_locations()
        )
        stock_packing = (
            self.sudo()
            .env["stock.picking"]
            .with_context(
                {
                    "restricted_picking_type_code": "outgoing",
                }
            )
            .create(
                [
                    {
                        **stock_packing_values,
                        "partner_id": self.using_user.id,
                        "location_id": self.location_id.id,
                        "location_dest_id": customer_loc.id,
                        "origin": self.asset_number,
                        "picking_type_id": picking_type_id.id,
                        "move_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": self.product_id.name,
                                    "product_id": self.product_id.id,
                                    "product_uom_qty": 1,
                                    "location_id": self.location_id.id,
                                    "location_dest_id": customer_loc.id,
                                },
                            )
                        ],
                    }
                ]
            )
        )
        stock_packing.button_validate()
        self.write(
            {
                "item_product": stock_packing.id,
                "state": "running",
                "history_id": [
                    (
                        0,
                        0,
                        {
                            "asset_id": self.id,
                            "assign_id": self.using_user.id,
                            "user_id": self.env.user.partner_id.id,
                            "action": "running",
                            "date": datetime.now(),
                            "inventory_id": stock_packing.id,
                            "description": f"{stock_packing.name} Assign To {self.using_user.name}",
                        },
                    )
                ],
            }
        )

    def to_return(self):
        return {
            "name": "Returned",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "asset.return.wizard",
            "views": [
                (self.env.ref("dhs_asset_mgt.view_asset_return_wizard_form").id, "form")
            ],
            "context": {"default_asset_id": self.id},
            "target": "new",
        }

    def to_retired(self):
        return {
            "name": "Retired(Scrap)",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "asset.retired.wizard",
            "views": [
                (
                    self.env.ref("dhs_asset_mgt.view_asset_retired_wizard_form").id,
                    "form",
                )
            ],
            "context": {"default_asset_id": self.id},
            "target": "new",
        }

    def to_reassignment(self):
        view = self.env.ref("dhs_asset_mgt.view_asset_reassignment_wizard_form")
        return {
            "name": "Reassignment",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "asset.reassignment.wizard",
            "views": [(view.id, "form")],
            "context": {"default_asset_id": self.id},
            "target": "new",
        }

    # ---------------------------------------------------
    #  CRUDS
    # ---------------------------------------------------
    @api.model
    def create_from_rpc(self, data):
        res = self.create(data)
        for record in res:
            record.to_running()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["asset_number"] = self.env["ir.sequence"].next_by_code(
                "asset.component.sequence"
            )
        return super().create(vals_list)

    def write(self, values):
        res = super(AssetComponent, self).write(values)
        self.env["ir.rule"].clear_caches()
        return res

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("you can only remove content when it is in draft status ")
                )
        return super(AssetComponent, self).unlink()

    # @api.model
    # def search(self, domain, offset=0, limit=None, order=None):
    #     res = super(AssetComponent, self).search(domain, offset=offset, limit=limit, order=order)
    #     res.get_last_action()
