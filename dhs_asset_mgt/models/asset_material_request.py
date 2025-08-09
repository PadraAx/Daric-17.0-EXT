
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


def apply_notification(method):
    def inner(obj):
        method(obj)
        return {'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'type': 'danger' if obj.state == "deraft" else 'success',
                           'title': _("Successfully!"),
                           'message': _(f"Status changed into {obj.state}"),
                           'next': {'type': 'ir.actions.act_window_close'},
                           }
                }
    inner.__wrapped__ = method
    return inner


class MaterialRequestProduct(models.Model):
    _name = "material.request.product"
    _description = "Material request"

    @api.constrains('quantity')
    def check_quantity(self):
        for record in self:
            if record.quantity > record.product_qty_available:
                raise UserError("The quantity should be less than the on-hand quantity")
            if record.quantity <= 0:
                raise UserError("The quantity should be greater than zero")

    @api.depends('product_id', 'request_location_id')
    def get_product_qty_available(self):
        for record in self:
            qty = 0
            if record.product_id and record.request_location_id:
                qty = self.env['stock.quant']._get_available_quantity(record.product_id, record.request_location_id)
            record.product_qty_available = qty

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.product_id.name}"

    material_request_id = fields.Many2one('material.request', "Material Request")
    request_location_id = fields.Many2one(related='material_request_id.location_id')
    product_id = fields.Many2one('product.product', "Product")
    quantity = fields.Float("Quantity")
    product_qty_available = fields.Float('On Hand Quantity', compute="get_product_qty_available", readonly=True)


class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = "create_date desc"

    def get_location_domain(self):
        domain = [('replenish_location', '=', True)]
        if not self.env.user.has_group('dhs_asset_mgt.group_it_asset_admin'):
            domain.append(('user_ids', 'in', self.env.user.id))
        return domain

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.matreial_number

    def _get_has_access(self):
        for record in self:
            record.has_access = True
            # if record.state == 'publish':
            #     record.has_access = True
            # elif self.env.user.has_group('knowledge_ext.group_knowledge_supervisor') and record.state in ('supervisor', 'final', 'rejected', 'expert'):
            # record.has_access = True

    matreial_number = fields.Char(string='Refrence Number')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, required=True,
                                 default=lambda s: s.env.company.id, index=True)
    location_id = fields.Many2one('stock.location', "Source Location", domain=get_location_domain,
                                  store=True, precompute=True, check_company=True, required=True)
    using_user = fields.Many2one("res.partner", string="Asignee", tracking=True, store=True,
                                 check_company=True, required=True, compute='item_product_user_on_change',)
    note = fields.Text()
    operation_reference = fields.Many2one('stock.picking', 'Operation Reference')
    material_request_product = fields.One2many(
        'material.request.product', 'material_request_id', 'Materials Asset Product', required=True)
    asset_ids = fields.One2many('asset.component', 'material_request_id',
                                'Assets', readonly=True, index=True, required=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("createdAsset", "Created Asset"),
            ("deliverd", "Deliverd"),
        ],
        default="draft",
        tracking=True,
        index=True,
    )
    has_access = fields.Boolean(compute="_get_has_access")

    # ---------------------------------------------------
    #  BUTTONS
    # ---------------------------------------------------

    @apply_notification
    def to_draft(self):
        self.write({'state': 'draft'})
        # self.send_email_notification('knowledge_ext.mail_template_knowledge_draft')

    @apply_notification
    def to_created_asset(self):
        if(not self.material_request_product):
            raise UserError("Please select a product and rate")
        for material_request_product in self.material_request_product:
            for count in range(0, int(material_request_product.quantity)):
                self.sudo().env['asset.component'].create([{
                    'using_user': self.using_user.id,
                    'material_request_id': self.id,
                    'product_id': material_request_product.product_id.id,
                    'component_note': self.note,
                    'company_id': self.company_id.id,
                    'location_id': self.location_id.id
                }])

        self.write({'state': 'createdAsset'})

    @apply_notification
    def to_deliverd(self):
        for asset in self.asset_ids:
            asset.to_running()
        self.write({'state': 'deliverd'})

    # ---------------------------------------------------
    #  CRUDS
    # ---------------------------------------------------

    @api.model
    def create(self, vals):
        matreial_number = self.env['material.request'].search([], order='id desc', limit=1)
        if(matreial_number):
            vals['matreial_number'] = "Material-{code:05d}".format(
                code=int(matreial_number.matreial_number.replace("Material-", ""))+1)
        else:
            vals['matreial_number'] = "Material-{code:05d}".format(code=int(1))

        return super(MaterialRequest, self).create(vals)

    def write(self, values):
        for record in self:
            if(not record.matreial_number):
                values['matreial_number'] = "Material-{code:05d}".format(
                    code=int(self.env['material.request'].search_count([])+1))
                res = super(MaterialRequest, self).write(values)
            else:
                res = super(MaterialRequest, self).write(values)
        self.env['ir.rule'].clear_caches()
        return res
