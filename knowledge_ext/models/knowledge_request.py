# -*- coding: utf-8 -*-
from random import randint
from operator import itemgetter
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


def apply_notification(method):
    def inner(obj):
        method(obj)
        return {'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'type': 'danger' if obj.state == "rejected" else 'success',
                           'title': _("Successfully!"),
                           'message': _(f"Status changed into {obj.state}"),
                           'next': {'type': 'ir.actions.act_window_close'},
                           }
                }
    inner.__wrapped__ = method
    return inner


REQUEST_MAIL_TEMPLATE = {
    'draft': ['knowledge_ext.mail_template_knowledge_draft'],
    'supervisor': ['knowledge_ext.mail_template_knowledge_supervisor'],
    'ambassador': ['knowledge_ext.mail_template_knowledge_ambassador',
                   'knowledge_ext.mail_template_knowledge_worker_notification'],
    'expert': ['knowledge_ext.mail_template_knowledge_expert',
               'knowledge_ext.mail_template_knowledge_worker_notification'],
    'final': ['knowledge_ext.mail_template_knowledge_final'],
    'publish': ['knowledge_ext.mail_template_knowledge_publish'],
    'rejected': ['knowledge_ext.mail_template_knowledge_rejected'],
}


class KnowledgeRequest(models.Model):
    _name = 'knowledge.request'
    _description = 'Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"

    @api.depends('article_id')
    def _get_name(self):
        for item in self:
            item.name = f'{item.sudo().article_id.name}'

    def _get_has_access(self):
        for record in self:
            record.has_access = False
            if record.state == 'publish':
                record.has_access = False
            elif record.create_uid.id == self.env.user.id and record.state == 'draft':
                record.has_access = True
            elif record.state == 'ambassador' and self.env.user.id in record.ambassador_ids.ids:
                record.has_access = True
            elif record.state == 'expert' and self.env.user.id in record.expert_ids.ids:
                record.has_access = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.has_access = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_supervisor') and record.state in ('supervisor', 'final', 'rejected', 'expert'):
                record.has_access = True

    def _get_access_content(self):
        for record in self:
            record.access_content = False
            if record.state == 'publish':
                record.access_content = False
            elif record.create_uid.id == self.env.user.id and record.state == 'draft':
                record.access_content = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_content = True
            elif record.state == 'expert' and self.env.user.id in record.expert_ids.ids:
                record.access_content = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_supervisor') and record.state in ('supervisor', 'final', 'rejected', 'expert'):
                record.access_content = True

    def _get_access_ambassador_expert_ids(self):
        for record in self:
            record.access_ambassador_expert_ids = False
            if record.state == 'publish':
                record.access_ambassador_expert_ids = False
            elif record.state == 'supervisor' and self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
                record.access_ambassador_expert_ids = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_ambassador_expert_ids = True

    def _get_access_parent_id(self):
        for record in self:
            record.access_parent_id = False
            if record.state == 'publish':
                record.access_parent_id = False
            elif (record.state in ('supervisor', 'final') and self.env.user.has_group('knowledge_ext.group_knowledge_supervisor')):
                record.access_parent_id = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_parent_id = True

    def _get_access_evaluation_ids(self):
        for record in self:
            record.access_evaluation_ids = False
            if self.env.user.id in record.expert_ids.ids:
                record.access_evaluation_ids = True
            elif self.env.user.has_group('knowledge_ext.group_knowledge_manager') or self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
                record.access_evaluation_ids = True

    @api.depends('has_access')
    def _get_access_tag_ids(self):
        for record in self:
            record.access_tag_ids = False
            if self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_tag_ids = True
            elif record.state in ('draft', 'supervisor', 'final') and record.has_access:
                record.access_tag_ids = True

    def _get_access_ambassador_checklist_ids(self):
        for record in self:
            record.access_ambassador_checklist_ids = False
            if record.state == 'publish':
                record.access_ambassador_checklist_ids = False
            if self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_ambassador_checklist_ids = True
            elif record.state == 'ambassador' and self.env.user.id in record.ambassador_ids.ids:
                record.access_ambassador_checklist_ids = True

    def _get_access_avg_ids(self):
        for record in self:
            record.access_avg_ids = False
            if self.env.user.has_group('knowledge_ext.group_knowledge_supervisor') or self.env.user.has_group('knowledge_ext.group_knowledge_manager'):
                record.access_avg_ids = True

    def _get_rec_url(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('knowledge_ext.knowledge_request_action', raise_if_not_found=False)
        link = """{}/web#id={}&view_type=form&model=knowledge.request&action={}""".format(
            web_base_url, self.id, action_id.id)
        return link

    def _get_total_score(self):
        for record in self:
            if sum([item.factor for item in record.avg_ids]) == 0:
                record.total_score = 0
            else:
                record.total_score = sum([item.score_avg*item.score_id.factor for item in record.avg_ids]
                                         ) / sum([item.factor for item in record.avg_ids]) or 0

    @api.constrains('state')
    def check_state_email(self):
        for record in self:
            templates = REQUEST_MAIL_TEMPLATE.get(record.state, [])
            for template in templates:
                self.send_email_notification(template)

    # ---------------------------------------------------
    #  Fields
    # ---------------------------------------------------

    name = fields.Char(string='Name', compute="_get_name", store=True, precompute=True)
    requester = fields.Many2one('res.users', default=lambda self: self.env.user.id, required=True, readonly=True)
    article_id = fields.Many2one('knowledge.article', string='Article', required=True, readonly=True)
    expert_ids = fields.Many2many('res.users', 'knowledge_user_expert', 'request_id', 'user_id', string="Expert Users",
                                  domain=lambda self: [('groups_id', 'in', self.env.ref('knowledge_ext.group_knowledge_expert').id)])
    ambassador_ids = fields.Many2many('res.users', 'knowledge_user_ambassador', 'request_id', 'user_id', string="Ambassador Users",
                                      domain=lambda self: [('groups_id', 'in', self.env.ref('knowledge_ext.group_knowledge_ambassador').id)])
    parent_article_id = fields.Many2many('knowledge.article', 'knowledge_request_parent_article', 'request_id', 'article_id', string='Knowledge Tree',
                                         domain="[('category', '=', 'workspace'), ('is_template', '=', False)]")
    state = fields.Selection([('draft', "Draft"),
                              ('supervisor', "Supervisor Review"),
                              ('ambassador', "Ambassador Review"),
                              ('expert', "Expert Review"),
                              ('final', "Final Review"),
                              ('publish', "Publish"),
                              ('rejected', "Rejected")], default='draft', required=True, string='State', tracking=True)
    content = fields.Html(string="Content")
    ambassador_checklist_ids = fields.One2many(
        'knowledge.request.ambassador.item', 'request_id', string='Ambassador Check List')
    evaluation_ids = fields.One2many('knowledge.request.score', 'request_id', string='Evaluation')
    avg_ids = fields.One2many('knowledge.request.score.avg', 'request_id', string='Evaluation Avarage')
    active = fields.Boolean('Active', default=True,
                            help="By unchecking the active field, you may hide an version you will not use.")
    # Access field
    has_access = fields.Boolean(compute="_get_has_access")
    access_content = fields.Boolean(compute='_get_access_content', string='Access Content')
    access_ambassador_expert_ids = fields.Boolean(
        compute='_get_access_ambassador_expert_ids', string='Access Assign Ambassador and Expert')
    access_parent_id = fields.Boolean(compute='_get_access_parent_id', string='Access Knowledge Tree')
    access_evaluation_ids = fields.Boolean(compute='_get_access_evaluation_ids', string='Access Evaluation ids')
    access_tag_ids = fields.Boolean(compute='_get_access_tag_ids', string='Access Tag ids')
    access_ambassador_checklist_ids = fields.Boolean(
        compute='_get_access_ambassador_checklist_ids', string='Access Ambassador Checklist ids')
    access_avg_ids = fields.Boolean(compute='_get_access_avg_ids', string='Access Average ids')
    # Extra Fields :
    icon = fields.Char(string='Emoji')
    cover_image_id = fields.Many2one("knowledge.cover", string='Article cover')
    cover_image_url = fields.Char(related="cover_image_id.attachment_url", string="Cover url")
    cover_image_position = fields.Float(string="Cover vertical offset")
    tag_ids = fields.Many2many('knowledge.tag', string='Tags')
    total_score = fields.Float(string="Total Score:", compute="_get_total_score")
    last_edition_uid = fields.Many2one("res.users", string="Last Edited by", readonly=True, copy=False)
    last_edition_date = fields.Datetime(string="Last Edited on", readonly=True, copy=False)
    parent_id = fields.Many2one("knowledge.article", string="Parent Article", tracking=30, ondelete="cascade")
    article_properties_definition = fields.PropertiesDefinition('Article Item Properties')
    article_properties = fields.Properties(
        'Properties', definition="parent_id.article_properties_definition", copy=True)
    html_field_history_metadata = fields.Char(compute="_get_html_field_history_metadata")

    # ---------------------------------------------------
    #  Functionality
    # ---------------------------------------------------

    def _get_html_field_history_metadata(self):
        for item in self:
            item.html_field_history_metadata = f'{item.sudo().article_id.name}'
        return

    def _get_reject_emails(self):
        ref_group = self.env.ref('knowledge_ext.group_knowledge_supervisor')
        supervisour_user = self.env['res.users'].search([('groups_id', 'in', [ref_group.id])])
        email_list = [item for item in supervisour_user.partner_id.mapped("email") if item]
        if self.create_uid.partner_id.email:
            email_list.append(self.create_uid.partner_id.email)
        return ",".join(set(email_list))

    def _get_supervisor_emails(self):
        ref_group = self.env.ref('knowledge_ext.group_knowledge_supervisor')
        supervisour_user = self.env['res.users'].search([('groups_id', 'in', [ref_group.id])])
        email_list = [item for item in supervisour_user.partner_id.mapped("email") if item]
        return ",".join(set(email_list))

    def _get_ambassador_emails(self):
        email_list = [item for item in self.ambassador_ids.partner_id.mapped("email") if item]
        return ",".join(set(email_list))

    def _get_expert_emails(self):
        email_list = [item for item in self.expert_ids.partner_id.mapped("email") if item]
        return ",".join(set(email_list))

    def send_email_notification(self, template):
        template_obj = self.env.ref(template, raise_if_not_found=False)
        if template_obj:
            for obj in self:
                template_obj.sudo().send_mail(obj.id, force_send=True)

# ---------------------------------------------------
#  Buttons
# ---------------------------------------------------

    @apply_notification
    def to_draft(self):
        self.write({'state': 'draft'})

    @apply_notification
    def to_supervisor(self):
        self.write({'state': 'supervisor'})

    @apply_notification
    def to_ambassador(self):
        if (not self.expert_ids or not self.ambassador_ids) and self.state == 'supervisor':
            raise ValidationError('Supervisor should assign both an Expert and Ambassador to the article.')
        self.write({'state': 'ambassador'})
        if not self.sudo().ambassador_checklist_ids:
            self.sudo().write({'ambassador_checklist_ids':  [
                (0, 0, {'ambassador_item_id': item.id}) for item in self.env['knowledge.ambassador.item'].search([])]})

    @apply_notification
    def to_expert(self):
        if self.ambassador_checklist_ids.filtered(lambda r: not r.done):
            raise ValidationError('Ambassador should mark all checklist items.')
        self.write({'state': 'expert'})
        self.sudo().evaluation_ids.unlink()
        self.sudo().avg_ids.unlink()
        for user in self.expert_ids:
            self.sudo().write({'evaluation_ids':  [
                (0, 0, {'score_id': item.id, 'expert_id': user.id}) for item in self.env['knowledge.score'].search([])]})

    def to_final(self):
        self.write({'state': 'final'})
        data = self.sudo().env['knowledge.request.score'].read_group(
            [('request_id', '=', self.id)], ['score:avg', 'score_id'], ['score_id'])
        self.sudo().write({'avg_ids':  [(0, 0, {'score_id': r['score_id'][0], 'score_avg': r['score']}) for r in data]})

    @apply_notification
    def to_publish(self):
        if not (self.sudo().parent_article_id) and self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
            raise ValidationError('you should fill knowledge tree field!')
        self.write({'state': 'publish'})
        for each in self.sudo().parent_article_id:
            self.sudo().env['knowledge.article'].with_user(self.requester.id).with_context(by_pass=True, allowed_company_ids=[]).create({
                'name': self.name,
                'parent_id': each.id,
                'body': self.content,
                'icon': self.icon,
                'cover_image_id': self.cover_image_id.id,
                'category': 'workspace',
                'tag_ids': self.tag_ids.ids,
            })

    @apply_notification
    def to_rejected(self):
        self.write({'state': 'rejected'})

    def confirm(self):
        return {
            'name': _('Confirm button action'),
            "type": "ir.actions.act_window",
            "res_model": "wizard.supervisor.mark",
            "context": {"active_id": self.id, 'default_request_id': self.id},
            "view_mode": 'form',
            'target': 'new',
        }


# ---------------------------------------------------
#  Crud
# ---------------------------------------------------

    @api.model
    def create(self, vals):
        if (vals.get('expert_ids') == '' or vals.get('ambassador_ids') == '') and vals.get('state') == 'supervisor':
            raise ValidationError('Supervisor should assign both an Expert and Ambassador to the article.')
        if vals.get('ambassador_checklist_ids') == '' and vals.get('state') == 'ambassador':
            raise ValidationError('Ambassador should mark all checklist items.')
        res = super(KnowledgeRequest, self).create(vals)
        self.env['ir.rule'].clear_caches()
        return res

    def write(self, vals):
        if (vals.get('expert_ids') == '' or vals.get('ambassador_ids') == '') and vals.get('state') == 'supervisor':
            raise ValidationError('Supervisor should assign both an Expert and Ambassador to the article.')
        if vals.get('ambassador_checklist_ids') == '' and vals.get('state') == 'ambassador':
            raise ValidationError('Ambassador should mark all checklist items.')
        if vals.get('content'):
            self.message_post(body=_("The content was changed by %s", self.create_uid.name))
        res = super(KnowledgeRequest, self).write(vals)
        self.env['ir.rule'].clear_caches()
        return res
