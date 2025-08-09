# models/otp_verification.py
from odoo import models, fields, api
import random
import string
from datetime import datetime, timedelta

class OTPVerification(models.Model):
    _name = 'otp.verification'
    _description = 'OTP Verification for User Login'

    user_id = fields.Many2one('res.users', string="User")
    phone_number = fields.Char(string="Phone Number")
    otp_code = fields.Char(string="OTP Code", size=6)
    expire_time = fields.Datetime(string="Expiration Time")
    is_verified = fields.Boolean(string="Is Verified", default=False)

    def generate_otp(self):
        """Generate a 6-digit random OTP."""
        otp = ''.join(random.choices(string.digits, k=6))
        self.otp_code = otp
        # Set expiration time for 5 minutes
        self.expire_time = datetime.now() + timedelta(minutes=5)
        return otp

    def send_otp_sms(self, otp):
        """Send OTP code to the user's phone via SMS."""
        sms_ir = self.env['sms.ir']  # Assuming you have a sms.ir integration
        message = f"Your OTP code is: {otp}"
        sms_ir.send_sms(self.phone_number, message)
