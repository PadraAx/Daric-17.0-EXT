from odoo import models
from odoo.http import request

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(Http, self).session_info()

        # find help desk team
        team = self.env['helpdesk.team'].search([('use_website_helpdesk_form', '=', True)], limit=1)

        # get the base_url from the current request
        base_url = request.httprequest.host_url.rstrip('/')
        
        # ensure team and website_url exist
        if team and team.website_url:
            website_url = team.website_url.lstrip('/')
            result['support_url'] = f"{base_url}/{website_url}"
        else:
            result['support_url'] = base_url  # fallback to base_url if no team found

        return result
