from odoo import api, fields, models, _


class MailChimpLog(models.Model):
    _name = "mailchimp.log"
    _description = "Mailchimp Log"
    _order = 'id desc'

    name = fields.Char(string='Name', required=True, copy=False, default=lambda self: _('New'))
    type = fields.Selection([('error', 'Error')], required=True)
    during = fields.Char(string='During')
    log_line = fields.One2many('mailchimp.log.line', 'log_id', string='Log Lines', copy=True)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('name', _('New')) == _('New'):
                val['name'] = self.env['ir.sequence'].next_by_code('mailchimp.log') or _('New')
        return super(MailChimpLog, self).create(vals_list)


class MailChimpLogLine(models.Model):
    _name = "mailchimp.log.line"
    _description = "Mailchimp Log Line"

    name = fields.Char(string='Name', required=True)
    model_name = fields.Char(string='Model Name')
    res_id = fields.Integer(string="Id")
    log_id = fields.Many2one('mailchimp.log', string='Log', ondelete='cascade')
    description = fields.Text(string='Description')
    req_data = fields.Text('Request Data', default='{}', copy=False)

    def redirect_to_log_record(self):
        vals = {
            'domain': [('id', '=', self.res_id)],
            'name': "Contact",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.model_name,
            'type': 'ir.actions.act_window',
            'target': 'self',
        }
        return vals
