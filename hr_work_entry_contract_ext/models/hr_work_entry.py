# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import date
from collections import deque
from odoo import models, api, fields
from odoo.tools import float_round


class HrWorkEntry(models.Model):
    _inherit = 'hr.work.entry'
    _order = 'date_start desc'

# -------------------------------------------------------------------------
# Generate work Entry Job
# -------------------------------------------------------------------------

    def get_current_pay_periods(self):
        today = date.today()
        domain = [
            ('status', 'in', ['draft', 'open']),
            ('date_from', '<=', today),
            ('date_to', '>=', today)
        ]
        return self.env['hr.payroll.period'].search(domain)

    def _get_contracts(self, period):
        """
        Returns the contracts of the employee between date_from and date_to
        """
        domain = [('state', 'in', ['draft', 'open']),
                  ('company_id', '=', period.company_id.id),
                  ('work_entry_source', '=', 'rule_att'),
                  ('date_start', '<=', period.date_to),
                  '|',
                  ('date_end', '=', False),
                  ('date_end', '>=', period.date_from)
                  ]
        return self.env['hr.contract'].search(domain)

    def calculate_work_entries(self):
        periods = self.get_current_pay_periods()
        for period in periods:
            valid_contract = self._get_contracts(period)
            if valid_contract:
                valid_contract.with_context({'generate': True}).generate_work_entries(
                    period.date_from, period.date_to)
