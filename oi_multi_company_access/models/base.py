'''
Created on Jun 28, 2021

@author: Zuhair Hammadi
'''
from odoo import models, api, _
from odoo.exceptions import AccessError
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    _inherit = 'base'
    
    @api.model
    def check_access_rights(self, operation, raise_exception=True):    
        session_uid = request and hasattr('request', 'session') and request.session.uid  # @UndefinedVariable
        if not self.env.su and self.env.user.company_group_ids and session_uid and self.env.user.id == session_uid:
            company_ids = self._context.get('allowed_company_ids', [])
            if company_ids and self.env.user.company_id.ids != company_ids and self._name not in ['website', 'mail.channel.partner', 'mail.channel', 'res.lang', 'mail.channel.member']:                
                _logger.warning("model %s user company %s <> context company %s" % (self._name, self.env.user.company_id.ids, company_ids))
                raise AccessError(_("Access to unauthorized or invalid companies."))
            
        return super(Base, self).check_access_rights(operation, raise_exception = raise_exception)