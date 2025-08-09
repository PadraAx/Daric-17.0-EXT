# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import math
import time
from ast import literal_eval
from datetime import date, timedelta
from collections import defaultdict

from odoo import SUPERUSER_ID, _, api, Command, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.addons.web.controllers.utils import clean_action
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT,
    format_datetime,
    format_date,
    groupby,
)
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class AssetStockPicking(models.Model):
    _inherit = "stock.picking"

    location_id = fields.Many2one(
        "stock.location",
        "Source Location",
        compute="_compute_location_id",
        store=True,
        readonly=False,
        check_company=True,
        required=False,
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Destination Location",
        compute="_compute_location_id",
        store=True,
        precompute=True,
        readonly=False,
        check_company=True,
        required=False,
    )
    asset_component = fields.One2many(
        "asset.component", "item_product", string="Asset Component"
    )

    def _set_scheduled_date(self):
        for picking in self:
            asset = self._context.get("asset", False)
            if asset == "True":
                picking.move_ids.write({"date": picking.scheduled_date})
            else:
                if picking.state in ("done", "cancel"):
                    raise UserError(
                        _(
                            "You cannot change the Scheduled Date on a done or cancelled transfer."
                        )
                    )
                picking.move_ids.write({"date": picking.scheduled_date})
