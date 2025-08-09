# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import json
import re
import logging

from collections import defaultdict
from datetime import datetime, timedelta
from markupsafe import Markup
from urllib import parse
from werkzeug.urls import url_join
from odoo.addons.web_editor.tools import handle_history_divergence

from odoo import api, Command, fields, models, _
from odoo.addons.web.controllers.utils import clean_action
from odoo.exceptions import AccessError, ValidationError, UserError
from odoo.osv import expression
from odoo.tools import get_lang

_logger = logging.getLogger(__name__)


class Article(models.Model):
    _inherit = "knowledge.article"

    @api.depends('template_body')
    def _compute_template_preview(self):
        for template in self:
            template.template_preview = template.template_body

    def _get_is_publish(self):
        for record in self:
            record.is_publish = self.env['knowledge.request'].sudo().search([('article_id', '=', record.id)])

    def _get_access_create_icon(self):
        for record in self:
            record.access_create_icon = False
            if self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
                record.access_create_icon = True

    def _get_publish_date(self):
        for record in self:
            record.publish_date = self.env['knowledge.request'].sudo().search(
                [('article_id', '=', record.id)]).write_date

    def _get_total_score(self):
        for record in self:
            data = self.env['knowledge.request'].sudo().search([('article_id', '=', record.id)])
            if sum([item.factor for item in data.avg_ids]) == 0:
                record.total_score = 0
            else:
                record.total_score = sum([item.score_avg*item.score_id.factor for item in data.avg_ids]
                                         ) / sum([item.factor for item in data.avg_ids]) or 0

    # Fields
    publish_date = fields.Date(compute="_get_publish_date", string='Publish Date')
    total_score = fields.Integer(compute="_get_total_score", string='Total Score')

    cover_image_id = fields.Many2one("knowledge.cover", string='Article cover', domain=[('user_has_access','=',True)])
    
    is_publish = fields.Boolean(compute="_get_is_publish", string='Is Publish')
    tag_ids = fields.Many2many('knowledge.tag', string='Tags')
    department_ids = fields.Many2many('hr.department', string='departments')
    access_create_icon = fields.Boolean(compute='_get_access_create_icon', string='Access Create Icon')

    @api.depends_context('uid')
    @api.depends('internal_permission', 'article_member_ids.partner_id', 'article_member_ids.permission')
    def _compute_user_permission(self):
        super(Article, self)._compute_user_permission()
        for article in self:
            if article.category == 'workspace':
                if self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
                    article.user_permission = 'write'
                else:
                    permission = 'read'
                    if article.sudo().department_ids:
                        child_dep = article.sudo().department_ids.search(
                            [('id', 'parent_of', self.env.user.employee_id.department_id.id),
                                ('id', 'in', article.department_ids.ids)])
                        permission = 'read' if child_dep else 'none'
                    if article.parent_id.user_permission == 'none':
                        permission = 'none'
                    article.user_permission = permission
            if self._context.get('by_pass') and self._context['by_pass']:
                article.user_permission = 'write'

    @api.depends_context('uid')
    @api.depends('user_has_write_access')
    def _compute_user_can_write(self):
        super(Article, self)._compute_user_can_write()
        for article in self:
            if article.category == 'workspace':
                if self.env.user.has_group('knowledge_ext.group_knowledge_supervisor'):
                    article.user_can_write = True
                else:
                    article.user_can_write = False
            if self._context.get('by_pass') and self._context['by_pass']:
                article.user_can_write = True

    @api.model
    @api.returns('knowledge.article', lambda article: article.id)
    def article_template_create(self, values, parent, is_private):
        if parent:
            if not is_private and parent.category == "private":
                is_private = True
        else:
            # child do not have to setup an internal permission as it is inherited
            values['internal_permission'] = 'none' if is_private else 'write'

        if is_private:
            if parent and parent.category != "private":
                raise ValidationError(
                    _("Cannot create an article under article %(parent_name)s which is a non-private parent",
                      parent_name=parent.display_name)
                )
            if not parent:
                values['article_member_ids'] = [(0, 0, {
                    'partner_id': self.env.user.partner_id.id,
                    'permission': 'write'
                })]

        return self.create(values)

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        res = super(Article, self).search(domain, offset=offset, limit=limit, order=order)
        return isinstance(res, Article) and res.filtered(lambda r: r.user_has_access == True) or res

    def get_sidebar_articles(self, unfolded_ids=False):
        """ Get the data used by the sidebar on load in the form view.
        It returns some information from every article that is accessible by
        the user and that is either:
            - a visible root article
            - a favorite article or a favorite item (for the current user)
            - the current article (except if it is a descendant of a hidden
              root article or of an non accessible article - but even if it is
              a hidden root article)
            - an ancestor of the current article, if the current article is
              shown
            - a child article of any unfolded article that is shown
        """

        root_articles_domain = [
            ("parent_id", "=", False),
            ("is_template", "=", False)
        ]
        if self.env.user._is_internal():
            # Do not fetch articles that the user did not join (articles with
            # internal permissions may be set as visible to members only)
            root_articles_domain.append(("is_article_visible", "=", True))

        # Fetch root article_ids as sudo, ACLs will be checked on next global call fetching 'all_visible_articles'
        # this helps avoiding 2 queries done for ACLs (and redundant with the global fetch)
        root_articles_ids = self.env['knowledge.article'].sudo().search(root_articles_domain).ids

        favorite_articles_ids = self.env['knowledge.article.favorite'].sudo().search(
            [("user_id", "=", self.env.user.id), ('is_article_active', '=', True)]
        ).article_id.ids

        # Add favorite articles and items (they are root articles in the
        # favorite tree)
        root_articles_ids += favorite_articles_ids

        if unfolded_ids is False:
            unfolded_ids = []

        # Add active article and its parents in list of unfolded articles
        if self.is_article_visible:
            if self.parent_id:
                unfolded_ids += self._get_ancestor_ids()
        # If the current article is a hidden root article, show the article
        elif not self.parent_id and self.id:
            root_articles_ids += [self.id]

        all_visible_articles = self.get_visible_articles(root_articles_ids, unfolded_ids)

        return {
            "articles": all_visible_articles.read(
                ['name', 'icon', 'parent_id', 'category', 'is_locked', 'user_can_write',
                    'is_user_favorite', 'is_article_item', 'has_article_children', 'is_publish', 'access_create_icon'],
                None,  # To not fetch the name of parent_id
            ),
            "favorite_ids": favorite_articles_ids,
        }

    def write(self, vals):
        # Move under a parent is considered as a write on it (permissions, ...)
        _resequence = False
        if not self.env.user._is_internal() and not self.env.su:
            writable_fields = self._get_portal_write_fields_allowlist()
            if all(article.category == 'private' for article in self):
                # let non internal users re-organize their private articles
                # and send them to trash if they wish
                writable_fields |= {'active', 'to_delete', 'parent_id'}

            if vals.keys() - writable_fields:
                raise AccessError(_('Only internal users are allowed to modify this information.'))

        if 'body' in vals:
            if len(self) == 1:
                handle_history_divergence(self, 'body', vals)
            vals.update({
                'last_edition_date': fields.Datetime.now(),
                'last_edition_uid': self.env.user.id,
            })
        else:
            vals.pop('last_edition_date', False)
            vals.pop('last_edition_uid', False)

        if 'parent_id' in vals:
            parent = self.env['knowledge.article']
            if vals.get('parent_id') and self.filtered(lambda r: r.parent_id.id != vals['parent_id']):
                parent = self.browse(vals['parent_id'])
                try:
                    parent.check_access_rights('write')
                    parent.check_access_rule('write')
                except AccessError:
                    raise AccessError(_("You cannot move an article under %(parent_name)s as you cannot write on it",
                                        parent_name=parent.display_name))
            if 'sequence' not in vals:
                max_sequence = self._get_max_sequence_inside_parents(parent.ids).get(parent.id, -1)
                vals['sequence'] = max_sequence + 1
            else:
                _resequence = True

        result = super(models.Model, self).write(vals)

        # resequence only if a sequence was not already computed based on current
        # parent maximum to avoid unnecessary recomputation of sequences
        if _resequence:
            self.sudo()._resequence()

        return result

    @api.model
    def apply_new_template(self, template_id):
        template = self.env['knowledge.article'].browse(template_id)
        template.ensure_one()
        try:
            body = template._render_template()
        except:
            body = ''
        article = self.env['knowledge.article'].create({
            'article_properties': template.article_properties or {},
            'article_properties_definition': template.article_properties_definition,
            'body': body,
            'cover_image_id': template.cover_image_id.id,
            'full_width': template.full_width,
            'icon': template.icon,
            'name': template.template_name,
            'internal_permission': 'none',
            # 'is_article_item': True,
            'article_member_ids': [(0, 0, {
                'partner_id': self.env.user.partner_id.id,
                'permission': 'write',
            })],
            'category': 'private'})

        return article.id

    @api.model
    def get_user_attachment_ids(self):
        out = self.env["knowledge.article"].search([('user_can_read','=',True)]).cover_image_id.attachment_id.ids
        return out