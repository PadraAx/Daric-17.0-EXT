from odoo import models, fields, api
from odoo.http import request
from sms_ir import SmsIr

class SMSIntegration(models.Model):
    _name = 'sms.integration'
    _description = 'SMS Integration with Sms.ir'

    api_key = fields.Char('API Key', required=True)
    linenumber = fields.Char('Line Number', required=True)
    last_sent_sms = fields.Text('Last Sent SMS')

    def _get_sms_instance(self):
        """
        Returns an instance of the SmsIr API client using the configured API key and line number.
        Loads the API key and line number from ir.config_parameter.
        """
        # Load API Key and Line Number from ir.config_parameter
        api_key = request.env['ir.config_parameter'].sudo().get_param('sms_integration.api_key')
        linenumber = request.env['ir.config_parameter'].sudo().get_param('sms_integration.linenumber')

        # Check if the configuration values are available
        if not api_key or not linenumber:
            raise ValueError("API Key or Line Number is not set in the configuration")

        # Return an instance of the SmsIr client
        return SmsIr(api_key, linenumber)

    def send_sms(self, number, message):
        """
        Send SMS to a single number using the Sms.ir service.
        """
        sms_ir = self._get_sms_instance()
        try:
            result = sms_ir.send_sms(number, message, self.linenumber)
            self.last_sent_sms = f"Sent to {number}: {message}"
            return result
        except Exception as e:
            self.last_sent_sms = f"Error sending SMS: {str(e)}"
            return f"Error sending SMS: {str(e)}"

    def send_bulk_sms(self, numbers, message):
        """
        Send SMS to a list of numbers.
        """
        sms_ir = self._get_sms_instance()
        try:
            result = sms_ir.send_bulk_sms(numbers, message, self.linenumber)
            return result
        except Exception as e:
            return f"Error sending bulk SMS: {str(e)}"

    def send_verify_code(self, number, template_id, parameters):
        """
        Send a verification code SMS using a predefined template.
        """
        sms_ir = self._get_sms_instance()
        try:
            result = sms_ir.send_verify_code(number, template_id, parameters)
            return result
        except Exception as e:
            return f"Error sending verification code: {str(e)}"

    def get_account_credit(self):
        """
        Retrieve the SMS account credit balance from Sms.ir.
        """
        sms_ir = self._get_sms_instance()
        try:
            result = sms_ir.get_credit()
            return result
        except Exception as e:
            return f"Error retrieving credit: {str(e)}"
