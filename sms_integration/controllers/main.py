from odoo import http
from odoo.http import request
from odoo.addons.sms_integration.models.otp_verification import OTPVerification
from datetime import datetime, timedelta

class OTPLoginController(http.Controller):

    @http.route('/web/login', type='http', auth='public', website=True)
    def login(self, **kwargs):
        """Override the default login to add OTP functionality."""
        user_phone = kwargs.get('phone_number')
        otp_code = kwargs.get('otp_code')

        # Check if OTP login is enabled
        otp_enabled = request.env['ir.config_parameter'].sudo().get_param('sms_integration.otp_login_enabled')

        if otp_enabled:
            if otp_code:
                otp = request.env['otp.verification'].search([('phone_number', '=', user_phone)], limit=1)
                if otp and otp.otp_code == otp_code and datetime.now() < otp.expire_time:
                    # OTP is valid and not expired, authenticate the user
                    user = otp.user_id
                    user.sudo().write({'last_login': datetime.now()})
                    request.session.authenticate(request.env.cr.dbname, user.login, user.password)
                    otp.is_verified = True
                    return request.redirect('/web')
                else:
                    return request.render('sms_integration.otp_error_page', {'error_message': 'Invalid OTP or OTP expired.'})

            # If OTP isn't submitted, show OTP request page
            return request.render('sms_integration.otp_request_page', {'phone_number': user_phone})
        
        return request.render('website.login')

    @http.route('/web/send_otp', type='json', auth='public')
    def send_otp(self, phone_number):
        """Send OTP to the phone number."""
        otp_enabled = request.env['ir.config_parameter'].sudo().get_param('sms_integration.otp_login_enabled')

        if otp_enabled:
            # Check if the phone number is valid
            if not phone_number:
                return {'status': 'error', 'message': 'Phone number is required.'}

            # Generate OTP code
            otp_code = str(randint(1000, 9999))  # Generate a 4-digit OTP
            expire_time = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes

            # Create OTP verification record
            otp_verification = request.env['otp.verification'].create({
                'phone_number': phone_number,
                'otp_code': otp_code,
                'expire_time': expire_time,
            })

            # Send OTP via Sms.ir (integrated SMS service)
            sms_service = request.env['sms.integration'].sudo().search([], limit=1)
            if sms_service:
                sms_service.send_sms(phone_number, f'Your OTP code is: {otp_code}')

            return {'status': 'success', 'message': 'OTP sent successfully to the phone number.'}
        
        return {'status': 'error', 'message': 'OTP login is not enabled.'}
