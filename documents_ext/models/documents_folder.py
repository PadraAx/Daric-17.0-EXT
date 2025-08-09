# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime


class DocumentFolder(models.Model):
    _inherit = "documents.folder"
    # _rec_name = 'complete_name'
    
    read_users = fields.Many2many(
        string='Read Users',
        comodel_name='res.users',
        relation="read_users_rel", column1="main_users_id", column2="sub_users_id",
        tracking=True,
        store=True,
        readonly=False,
        copy=True,
    )
    write_users = fields.Many2many(
        string='Write Users',
        comodel_name='res.users',
        relation="write_users_rel", column1="main_users_id", column2="sub_users_id",
        tracking=True,
        store=True,
        readonly=False,
        copy=True,
    )
    workspace_administrator_ids = fields.Many2many( string='Workspace Administrator',
        comodel_name='res.users',
        relation="workspace_administrator_rel",
        tracking=True,
        store=True,
        readonly=False,
        copy=True)
    
    has_write_access = fields.Boolean('Document User Upload Rights', compute="_compute_has_write_access")
    has_workspace_administrator_access = fields.Boolean('Create Workspace', compute="_compute_has_workspace_administrator_access")
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)


    @api.depends('name', 'parent_folder_id.complete_name')
    def _compute_complete_name(self):
        for folder in self:
            if folder.parent_folder_id:
                folder.complete_name = '%s / %s' % (folder.parent_folder_id.complete_name, folder.name)
            else:
                folder.complete_name = folder.name

    @api.depends('group_ids', 'read_group_ids')
    @api.depends_context('uid')
    def _compute_has_write_access(self):
        current_user_id = self.env.uid
        current_user_groups_ids = self.env.user.groups_id
        has_write_access = self.user_has_groups('documents.group_documents_manager') or self.user_has_groups('documents_ext.group_documents_workspace_administrator')
        read_only =  self.user_has_groups('documents.group_documents_user')
        
        if has_write_access:
            self.has_write_access = True
            return
        for record in self:
            folder_has_groups = (not record.group_ids and not record.read_group_ids and not record.read_group_ids and not record.write_users and not read_only or ((record.group_ids & current_user_groups_ids) or (current_user_id in record.write_users.ids))) 
            record.has_write_access = folder_has_groups

    @api.depends('workspace_administrator_ids',)
    @api.depends_context('uid')
    def _compute_has_workspace_administrator_access(self):
        current_user_id = self.env.uid
        current_user_groups_ids = self.env.user.groups_id
        workspace_administrator = self.user_has_groups('documents.group_documents_manager')
        member_of_workspace_administrator =  self.user_has_groups('documents.group_documents_workspace_administrator')
        
        if workspace_administrator:
            self.has_workspace_administrator_access = True
            return
        if member_of_workspace_administrator:
            for record in self:
                folder_has_groups = (member_of_workspace_administrator and current_user_id in record.workspace_administrator_ids.ids) 
                record.has_workspace_administrator_access = folder_has_groups
            
    def _get_inherited_settings_as_vals(self):
        self.ensure_one()
        return {
            'group_ids': [(6, 0, self.group_ids.ids)],
            'read_group_ids': [(6, 0, self.read_group_ids.ids)],
            'read_users': [(6, 0, self.read_users.ids)],
            'write_users': [(6, 0, self.write_users.ids)],
            'workspace_administrator_ids': [(6, 0, self.parent_folder_id.workspace_administrator_ids.ids)],
            'user_specific': self.user_specific,
            'user_specific_write': self.user_specific_write,
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('create_from_search_panel'):
            for vals in vals_list:
                if 'sequence' not in vals:
                    # Folders created from the search panel are set as first
                    # child of their parent by default
                    vals['sequence'] = 0
                if 'parent_folder_id' in vals:
                    parent_folder = self.env['documents.folder'].browse(vals['parent_folder_id'])
                    # Set default values based on parent folder's attributes
                    vals['workspace_administrator_ids'] = parent_folder.workspace_administrator_ids    
                if 'folder_id' not in vals:
                    continue
                # Folders created from the search panel inherit the parent's rights.
                vals.update(self.browse(vals['folder_id'])._get_inherited_settings_as_vals())
        return super().create(vals_list)
