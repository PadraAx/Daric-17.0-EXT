'''
Created on Dec 26, 2021

@author: Zuhair Hammadi
'''
from odoo import models

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        res.update({
            'multi_company_access' : bool(self.env.user.company_group_ids)
            })
        return res
