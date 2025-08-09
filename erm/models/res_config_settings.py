import csv
import os
from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ERMSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_monetory_impact = fields.Boolean("Based on Monetory Impact")
    risk_appetite = fields.Integer(string='Risk Appetite', help="The organization’s willingness to accept a certain level of risk.", 
                                   config_parameter="erm.risk_appetite")
    risk_appetite_control = fields.Selection([('1', 'Do not let pass'),
                                              ('2', 'let pass'),], string='Risk Appetite Control', config_parameter="erm.risk_appetite_control")
    erm_standard = fields.Selection([
        ('iso_31000', 'ISO 31000'),
        ('coso_erm', 'COSO ERM Framework')
    ], string="ERM Standard", config_parameter="erm.erm_standard")

    def set_values(self):
        """
        Override to prevent setting changes if any master data is linked.
        """
        super(ERMSettings, self).set_values()
        if self._context.get('module') != 'erm':
            return  # Skip if not saving this module's settings
        
        # Collect related models and fields to check for linked records
        related_models = [
            {'model': 'erm.risk.assignment', 'field': 'category_id'},
            {'model': 'erm.risk.template', 'field': 'category_id'}, 
            {'model': 'erm.risk.assignment', 'field': 'risk_source_id'},
            {'model': 'erm.risk.template', 'field': 'risk_source_id'}, 
            {'model': 'erm.risk.assignment', 'field': 'affected_area_ids'},
             {'model': 'erm.risk.template', 'field': 'affected_area_id'},
            {'model': 'erm.risk.template', 'field': 'affected_area_id'}, 
        ]

        # Check for linked records
        for relation in related_models:
            model = self.env[relation['model']]
            field_name = relation['field']
            linked_records = model.search([(field_name, '!=', False)])
            if linked_records:
                raise UserError(
                    f"Cannot change the setting because records in {relation['model']} are linked to master data. "
                    f"Example record: {linked_records[0].display_name}"
                )

        # Proceed with setting the new value if no linked records exist
        # IrDefault = self.env['ir.default']
        
        # previous_standard =  self.env['ir.config_parameter'].sudo().get_param('erm.erm_standard')
        # IrDefault.set('res.config.settings', 'erm_standard', self.erm_standard)

        # if self.erm_standard != previous_standard:
        self._replace_master_data(self.erm_standard)
      

    def _replace_master_data(self, standard):
        """
        Replace master data only if no records are linked to the master data in related models.
        """
        # Collect all related models and their fields pointing to master data
        related_models = [
            {'model': 'erm.risk.assignment', 'field': 'category_id'},
            {'model': 'erm.risk.template', 'field': 'category_id'}, 
            {'model': 'erm.risk.assignment', 'field': 'risk_source_id'},
            {'model': 'erm.risk.template', 'field': 'risk_source_id'}, 
            {'model': 'erm.risk.assignment', 'field': 'affected_area_ids'},
            {'model': 'erm.risk.template', 'field': 'affected_area_id'}, 
            {'model': 'erm.risk.objective', 'field': 'category_id'},
        ]

        # Check if any records in related models are linked to the master data
        for relation in related_models:
            model = self.env[relation['model']]
            field_name = relation['field']
            linked_records = model.search([(field_name, '!=', False)])
            if linked_records:
                raise UserError(
                    f"Cannot replace master data because records in {relation['model']} are linked to it. "
                    f"Example record: {linked_records[0].display_name}"
                )

        # If no linked records, proceed to delete and reload master data
        existing_categories = self.env['erm.risk.category'].search([])
        existing_sources = self.env['erm.risk.source'].search([])
        existing_affected_areaes = self.env['erm.risk.affected.area'].search([])

        existing_categories.unlink()
        self.env['ir.sequence'].search([('code', '=', 'erm_risk_category.seq')]).write({'number_next': 1})
        existing_sources.unlink()
        existing_affected_areaes.unlink()
        self._import_csv_data(standard)

    def _import_csv_data(self, standard):
        module_path = os.path.dirname(os.path.abspath(__file__))

        # 1. Import Risk Category
        category_file = os.path.join(module_path, f'../data/erm_master_data_category_{standard}.csv')
        category_file_records = self._load_csv_to_dict(category_file)
        category_map = self._create_records_in_batch('erm.risk.category', category_file_records, 'name')

        # 2. Import Objective Category
        objective_category_file = os.path.join(module_path, f'../data/erm_master_data_objective_category_coso_erm.csv')
        objective_category_file_records = self._load_csv_to_dict(objective_category_file)
        objective_category_map = self._create_records_in_batch('erm.risk.objective.category', objective_category_file_records, 'name')

        # 3. Import Risk sources
        source_file = os.path.join(module_path, f'../data/erm_master_data_sources_{standard}.csv')
        source_records = self._load_csv_to_dict(source_file)
        for record in source_records:
            # record['category_id'] = category_map.get(record['category_id'])
            # Map subcategory's category_name to its ID
            category_name = record['category_id']
            category_id = category_map.get(category_name)
            if not category_id:
                raise UserError(f"Category '{category_name}' not found.")
            record['category_id'] = category_id
        source_map = self._create_records_in_batch('erm.risk.source', source_records, 'name')

        # 4. Import Affected Area
        affected_area_file = os.path.join(module_path, f'../data/erm_master_data_affected_area_{standard}.csv')
        affected_area_records = self._load_csv_to_dict(affected_area_file)
        for record in affected_area_records:
            # Map subcategory's category_name to its ID
            category_name = record['category_id']
            category_id = category_map.get(category_name)
            if not category_id:
                raise UserError(f"Category '{category_name}' not found.")
            record['category_id'] = category_id
        affected_area_map = self._create_records_in_batch('erm.risk.affected.area', source_records, 'name')

    def _load_csv_to_dict(self, file_path):
        """
        Load data from a CSV file and return it as a list of dictionaries.
        """
        if not os.path.exists(file_path):
            raise UserError(f"The file {file_path} does not exist!")

        with open(file_path, mode='r', encoding='utf-8-sig') as csv_file:
            return list(csv.DictReader(csv_file))

    def _create_records_in_batch1(self, model_name, records):
        """
        Create records in batch and return a mapping of external IDs to record IDs.
        """
        created_records = self.env[model_name].create(records)
        return {record['id']: created.id for record, created in zip(records, created_records)}
    
    def _create_records_in_batch(self, model_name, records, key_field):
        """
        Create records and map names to IDs.
        """
        created_records = self.env[model_name].create(records)
        # Map name to ID for relational fields
        return {getattr(record, key_field): record.id for record in created_records}
