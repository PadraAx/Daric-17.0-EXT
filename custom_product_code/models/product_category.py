import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = 'product.category'

    level_id = fields.Char(
        string='Level ID', size=2, 
        help="Enter a 1 or 2 character level ID for this category"
    )
    category_id = fields.Char(
        string='Category ID', compute='_compute_category_id', store=True
    )
    image = fields.Binary(
        string='Image', attachment=True, 
        help="Upload an image for this category"
    )
    description = fields.Html(
        string='Description', 
        help="Add a detailed description for this category"
    )

    @api.constrains('level_id', 'parent_id')
    def _check_level_id(self):
        """Ensure level_id is correctly set based on hierarchy under Marketplace."""
        for category in self:
            if not category._should_validate_level_id():
                continue

            expected_length = 2 if category._has_marketplace_parent() else 1

            if category.level_id and len(category.level_id) != expected_length:
                raise ValidationError(
                    f"Invalid Level ID for '{category.name}'. Expected {expected_length} characters."
                )

            _logger.info(f"Validated level_id for '{category.name}': {category.level_id}")

    @api.depends('parent_id', 'level_id')
    def _compute_category_id(self):
        """Generate category_id based on level_id and parent category, only if under Marketplace."""
        for category in self:
            if not category._should_generate_category_id():
                category.category_id = False
                continue

            parent_category_id = category.parent_id.category_id if category.parent_id else ""
            category.category_id = f"{parent_category_id}{category.level_id}"

            if len(category.category_id) > 7:
                raise ValidationError(f"Category ID '{category.category_id}' exceeds 7 characters.")

            _logger.info(f"Computed category_id for '{category.name}': {category.category_id}")

    def _should_validate_level_id(self):
        """Check if level_id validation is necessary."""
        return self._is_under_marketplace() and self.level_id

    def _should_generate_category_id(self):
        """Check if category_id should be computed."""
        return self._is_under_marketplace() and self.level_id

    def _has_marketplace_parent(self):
        """Check if parent category is 'Marketplace'."""
        return bool(self.parent_id and self.parent_id._is_marketplace())

    def _is_under_marketplace(self):
        """Check if the category is under the 'Marketplace' category."""
        marketplace = self._get_marketplace_category()
        return bool(marketplace and self._is_descendant_of(marketplace))

    def _is_marketplace(self):
        """Check if the current category itself is 'Marketplace'."""
        marketplace = self._get_marketplace_category()
        return bool(marketplace and self.id == marketplace.id)

    def _get_marketplace_category(self):
        """Safely fetch the 'Marketplace' category."""
        return self.env.ref('daric_marketplace.category_marketplace', raise_if_not_found=False)

    def _is_descendant_of(self, category):
        """Check if self is a descendant of the given category."""
        current = self
        while current:
            if current.id == category.id:
                return True
            current = current.parent_id
        return False

    @api.model
    def get_marketplace_category_domain(self):
        """Dynamically get the domain for Marketplace categories."""
        marketplace_category = self._get_marketplace_category()
        return [('parent_id', '=', marketplace_category.id)] if marketplace_category else []

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Dynamically restrict categories to those under Marketplace in the form view."""
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        marketplace_category = self._get_marketplace_category()
        if marketplace_category and view_type == 'form' and res.get('arch'):
            res['arch'] = self._restrict_parent_category(res['arch'], marketplace_category.id)

        return res

    def _restrict_parent_category(self, xml_arch, marketplace_id):
        """Modify the parent_id field to only allow categories under Marketplace."""
        try:
            doc = etree.XML(xml_arch)
            for field in doc.xpath("//field[@name='parent_id']"):
                field.set("domain", f"[('parent_id', '=', {marketplace_id})]")
            return etree.tostring(doc, encoding='unicode')
        except Exception as e:
            _logger.error(f"Error processing XML view: {e}")
            return xml_arch
