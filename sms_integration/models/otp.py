from odoo import models, fields, api
import random
from datetime import datetime, timedelta

class OTPRequest(models.Model):
    _name = 'otp.request'
    _description = 'OTP Request'
    
    user_id = fields.Many2one('res.users', string="User")
    phone_number = fields.Char(string="Phone Number")
    otp_code = fields.Char(string="OTP Code")
    request_time = fields.Datetime(string="Request Time", default=fields.Datetime.now)
    expires_at = fields.Datetime(string="Expires At")
    verified = fields.Boolean(string="Verified", default=False)
    
    def generate_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.expires_at = fields.Datetime.now() + timedelta(minutes=5)
        self.env['sms.ir.service'].send_sms(self.phone_number, f"Your OTP code is: {self.otp_code}")

class ResUsers(models.Model):
    _inherit = 'res.users'

    otp_enabled = fields.Boolean(string="Enable OTP Login", default=False)
