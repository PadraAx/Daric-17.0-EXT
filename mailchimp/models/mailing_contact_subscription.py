from odoo import api, fields, models, _

_get_status = [('subscribed', 'Subscribed'), ('unsubscribed', 'Unsubscribed'), ('cleaned', 'Cleaned'),
               ('pending', 'Pending'), ('transactional', 'Transactional'), ('archived', 'Archived')]

class MailingSubscription(models.Model):
    _inherit = 'mailing.subscription'

    @api.depends('list_id')
    def _compute_mailchimp_list_id(self):
        mailchimp_list_obj = self.env['mailchimp.lists']
        for record in self:
            list_id = mailchimp_list_obj.search([('odoo_list_id', '=', record.list_id.id)], limit=1)
            record.mailchimp_list_id = list_id.id

    mailchimp_id = fields.Char("MailChimp ID", readonly=True, copy=False)
    mailchimp_list_id = fields.Many2one("mailchimp.lists", compute="_compute_mailchimp_list_id", string="MailChimp List", store=True)
    md5_email = fields.Char("MD5 Email", readonly=True, copy=False)
    mail_list_status = fields.Selection(_get_status, string='Status(Mailchimp)', copy=False, default='subscribed')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'opt_out' in vals and not vals.get('unsubscription_date'):
                if vals['opt_out']:
                    vals['mail_list_status'] = 'unsubscribed'
            if vals.get('unsubscription_date'):
                vals['mail_list_status'] = 'unsubscribed'
        return super(MailingSubscription,self).create(vals_list)

    def write(self, vals):
        if 'opt_out' in vals and 'unsubscription_date' not in vals:
            if vals['opt_out']:
                vals['mail_list_status'] = 'unsubscribed'
        if vals.get('unsubscription_date'):
            vals['mail_list_status'] = 'unsubscribed'
        return super(MailingSubscription, self).write(vals)
