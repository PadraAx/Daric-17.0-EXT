from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    supply_source_id = fields.Char(string='Supply Source ID', copy=False, readonly=True)

    @api.constrains('supply_source_id')
    def _check_supply_source_id_length(self):
        """Ensure Supply Source ID is exactly 7 characters."""
        for record in self:
            if record.supply_source_id and len(record.supply_source_id) != 7:
                raise ValidationError("Supply Source ID must be exactly 7 characters long.")

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle category initialization and generate supply source ID"""
        category_cache = {}
        for vals in vals_list:
            self._initialize_category_id(vals, category_cache)
        
        partners = super().create(vals_list)

        for partner in partners:
            if self._is_supply_source_tag_selected(partner, category_cache):
                self._generate_supply_source_id_if_needed(partner)

        return partners

    def _initialize_category_id(self, vals, category_cache):
        """Ensure the 'Supply Source' and 'Supplier' tags are added to category_id."""
        supply_source_tag = self._get_or_create_category(_('Supply Source'), category_cache)
        supplier_tag = self._get_or_create_category(_('Supplier'), category_cache)

        existing_categories = self._get_category_ids_from_vals(vals)
        new_categories = list(set(existing_categories + [supply_source_tag.id, supplier_tag.id]))
        vals['category_id'] = [(6, 0, new_categories)]

    def _get_or_create_category(self, tag_name, category_cache):
        """Get or create a category by name, using a cache to reduce queries."""
        if tag_name not in category_cache:
            tag = self.env['res.partner.category'].search([('name', '=', tag_name)], limit=1)
            if not tag:
                tag = self.env['res.partner.category'].create({'name': tag_name})
            category_cache[tag_name] = tag
        return category_cache[tag_name]

    def _get_category_ids_from_vals(self, vals):
        """Extract category IDs from vals."""
        return vals.get('category_id', [(6, 0, [])])[0][2]

    def _generate_supply_source_id_if_needed(self, partner):
        """Generate a Supply Source ID if necessary."""
        if not partner.supply_source_id:
            partner.supply_source_id = self._generate_supply_source_id()

    def _generate_supply_source_id(self):
        """Generate a unique 7-digit Supply Source ID."""
        last_id = self.env['res.partner'].search([], order='supply_source_id desc', limit=1).supply_source_id
        new_id = str(int(last_id) + 1 if last_id and last_id.isdigit() else 1).zfill(7)
        return new_id

    def _is_supply_source_tag_selected(self, partner, category_cache):
        """Check if the 'Supply Source' tag is selected for the partner."""
        supply_source_tag = self._get_or_create_category(_('Supply Source'), category_cache)
        return supply_source_tag in partner.category_id

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Ensure Supply Source ID is set if the category includes 'Supply Source'."""
        category_cache = {}
        supply_source_tag = self._get_or_create_category(_('Supply Source'), category_cache)
        for partner in self:
            if supply_source_tag in partner.category_id and not partner.supply_source_id:
                raise ValidationError("Please provide a valid Supply Source ID for this partner.")

    def action_save(self):
        """Custom save action."""
        self.ensure_one()
        self.write({'name': self.name})
        return True
