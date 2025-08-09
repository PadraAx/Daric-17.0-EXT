# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import json
import logging
from datetime import datetime

from odoo import _, api, models
from odoo.exceptions import ValidationError, UserError, AccessError, MissingError
# from openerp.http import request # casey?

_logger = logging.getLogger(__name__)


def normalize_data(data):
    if not isinstance(data, (list, tuple)):
        data = [data]
    out = [{key: str(value) for key, value in rec.items() if not (isinstance(value, bytes) or (isinstance(value, str) and len(value) > 2000))} for rec in data]
    return out


class AuditBase(models.AbstractModel):
    _inherit = 'base'

# -------------------------------------------------------------------------
# FUNCTIONALITY
# -------------------------------------------------------------------------

    def get_model_black_list(self):
        return ['^ir.', '^mail', 'audit.log', '^bus']

    def get_model_include_list(self):
        return ['hr.contract']

    @api.model
    def is_model_black(self, read=False):
        model_name = self._name
        black_list = self.get_model_include_list() if read else self.get_model_black_list()
        for pattern in black_list:
            if re.match(pattern, model_name):
                return True
        return False

    @api.model
    def get_write_last_data(self, value):
        values = []
        for record in self:
            out = {}
            for field in value.keys():
                field_value = getattr(self.sudo(), field)
                if isinstance(field_value, bytes):
                    continue
                try:
                    if hasattr(field_value, 'id'):
                        field_name_display = f'{field}/display'
                        out[field] = field_value.ids
                        out[field_name_display] = field_value.display_name if hasattr(
                            field_value, 'display_name') else False
                    else:
                        out[field] = str(field_value)
                except:
                    out[field] = field_value
            values.append(out)
        return values

    @api.model
    def get_unlink_log_data(self):
        model_fields = self._fields.keys()
        values = []
        for record in self:
            out = {}
            for field in model_fields:
                field_name = field
                field_value = getattr(record.sudo(), str(field))
                if isinstance(field_value, bytes):
                    continue
                try:
                    if hasattr(field_value, 'id'):
                        field_name_display = f'{field}/display'
                        out[field_name] = field_value.ids
                        out[field_name_display] = field_value.display_name if hasattr(
                            field_value, 'display_name') else False
                    else:
                        out[field_name] = str(field_value)
                except:
                    out[field_name] = field_value
            values.append(out)
        return values

    # -------------------------------------------------------------------------
    # FUNCTIONALITY
    #     insertion
    # -------------------------------------------------------------------------

    def insert_log(self, old_value, new_value, method):
        new_value = normalize_data(new_value)
        old_value = normalize_data(old_value)

        if method=='write' and len(new_value) == 1 and new_value[0] == {}:
            return False

        model_id = self.env['ir.model'].sudo()._get_id(self._name)
        values = {
            'new_value': json.dumps(new_value),
            'old_value': json.dumps(old_value),
            'method': method,
            'model_id': model_id,
            'res_ids': json.dumps(self.ids),
        } 
        self.env['audit.log'].create_user_log(values)

    def insert_create_log_data(self, data):
        self.insert_log({}, data, 'create')

    def insert_write_log_data(self, old_data, new_data):
        self.insert_log(old_data, new_data, 'write')

    def insert_unlink_log_data(self, data):
        self.insert_log(data, {}, 'unlink')

    def insert_read_log_data(self, data):
        self.insert_log(data, {}, 'read')

# -------------------------------------------------------------------------
# ORM METHODS
# -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        res = False
        if self.is_model_black(read=False):
            return super(AuditBase, self).create(vals_list)
        res = super(AuditBase, self).create(vals_list)
        try:
            if res.ids:
                res.insert_create_log_data(vals_list)
            return res
        except Exception as e:
            _logger.error(f"--Create User Base-- {str(e)}")
            if not res:
                return super(AuditBase, self).create(vals_list)
            return res

    def write(self, vals):
        if self.is_model_black(read=False):
            return super(AuditBase, self).write(vals)
        try:
            if self.ids:
                old_write_value = self.get_write_last_data(vals)
        except Exception as e:
            _logger.error(f"--Write User Base-- {str(e)}")
            return super(AuditBase, self).write(vals)

        res = super(AuditBase, self).write(vals)
        
        try:
            if self.ids:
                self.insert_write_log_data(old_write_value, vals)
            return res
        except Exception as e:
            _logger.error(f"--Write User Base-- {str(e)}")
            return super(AuditBase, self).write(vals)

    def unlink(self):
        res = False
        if self.is_model_black(read=False):
            return super().unlink()
        try:
            if self.ids:
                unlink_data_log = self.get_unlink_log_data()
        except Exception as e:
            _logger.error(f"--Unlink User Base-- {str(e)}")
            if not res:
                return super().unlink()
            return res

        res = super().unlink()
        
        try:
            if self.ids:
                self.insert_unlink_log_data(unlink_data_log)
            return res
        except Exception as e:
            _logger.error(f"--Unlink User Base-- {str(e)}")
            if not res:
                return super().unlink()
            return res

    def read(self, fields=None, load='_classic_read'):
        if not self.is_model_black(read=True):
            return super(AuditBase, self).read(fields, load)
        res = super(AuditBase, self).read(fields, load)
        try:
            if self.ids:
                self.insert_read_log_data(dict.fromkeys(fields))
            return res
        except Exception as e:
            _logger.error(f"--Read User Base-- {str(e)}")
            return super(AuditBase, self).read(fields, load)
