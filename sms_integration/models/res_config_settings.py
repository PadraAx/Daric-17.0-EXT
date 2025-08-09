from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # OTP Login configuration
    otp_login_enabled = fields.Boolean(string="Enable OTP Login", default=False)

    # SMS Integration configuration
    sms_api_key = fields.Char(string="API Key", config_parameter='sms_integration.api_key')
    sms_linenumber = fields.Char(string="Line Number", config_parameter='sms_integration.linenumber')
