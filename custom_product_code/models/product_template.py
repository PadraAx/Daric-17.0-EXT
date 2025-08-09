from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_code = fields.Char(string='Product Code', compute='_compute_product_code', store=True)
    supply_source_id = fields.Many2one('res.partner', string='Supply Source', required=True)

    @api.depends('categ_id', 'categ_id.custom_id', 'supply_source_id')
    def _compute_product_code(self):
        """ Compute a unique product code based on category and supply source """
        for product in self:
            product.product_code = product._generate_product_code()

    def _generate_product_code(self):
        """ Generate and return a unique product code for a product """
        if not self._is_valid_category():
            return False

        category_code = self._get_category_code()
        supply_code = self._get_supply_code()
        base_code = f"{category_code}{supply_code}"
        new_serial = self._get_next_serial(base_code)

        return f"{base_code}{new_serial}"

    def _is_valid_category(self):
        """ Check if the product category and its custom ID are valid """
        return bool(self.categ_id and hasattr(self.categ_id, 'custom_id') and self.categ_id.custom_id)

    def _get_category_code(self):
        """ Return the 7-character padded category code """
        return self.categ_id.custom_id.ljust(7, '0') if self.categ_id and self.categ_id.custom_id else '0000000'

    def _get_supply_code(self):
        """ Validate and return the supply source code """
        if not self.supply_source_id or not hasattr(self.supply_source_id, 'supply_source_id'):
            raise ValidationError("The selected partner does not have a valid Supply Source ID.")
        return str(self.supply_source_id.supply_source_id)

    def _get_next_serial(self, base_code):
        """ Find the next available serial number for the product code """
        domain = [('product_code', '=like', base_code + '%')]
        if self.id and isinstance(self.id, int):
            domain.append(('id', '!=', self.id))

        existing_products = self.env['product.template'].search(domain)
        existing_serials = []
        
        for prod in existing_products:
            serial_part = prod.product_code[len(base_code):] if prod.product_code else ''
            if serial_part.isdigit():
                existing_serials.append(int(serial_part))

        return str(max(existing_serials, default=0) + 1).zfill(4)

    @api.model
    def create(self, vals):
        """ Ensure product_code is generated before saving the product """
        record = super().create(vals)
        record.with_context(skip_product_code_update=True)._compute_product_code()
        return record

    def write(self, vals):
        """ Ensure product_code is updated on changes but prevent infinite recursion """
        result = super().write(vals)
        if not self.env.context.get('skip_product_code_update'):
            self.with_context(skip_product_code_update=True)._compute_product_code()
        return result
