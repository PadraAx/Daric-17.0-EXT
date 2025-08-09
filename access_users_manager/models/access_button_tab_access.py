# -*- coding: utf-8 -*-
from odoo import api, fields, models
from lxml import etree
from odoo.exceptions import ValidationError
from bs4 import BeautifulSoup


class ButtonTabAccess(models.Model):
    _name = 'button.tab.access'
    _description = 'Button Tab Access'

    access_model_id = fields.Many2one('ir.model', string='Model', domain="[('id', 'in', access_profile_domain_model )]")
    access_model_name = fields.Char(string='Model Name', related='access_model_id.model', readonly=True, store=True)
    access_hide_button_ids = fields.Many2many('button.tab.data', 'button_hide_rel_ah', 'button_id', 'user_id',
                                          string='Hide Button')
    access_kanban_button_ids = fields.Many2many('button.tab.data', 'link_hide_rel_ah', 'link_id', 'user_link_id',
                                            string='Hide Kanban Button')
    access_hide_tab_ids = fields.Many2many('button.tab.data', string='Hide Tab')
    access_user_manager_id = fields.Many2one('user.management', string='Rule')
    access_profile_domain_model = fields.Many2many('ir.model', related='access_user_manager_id.access_profile_domain_model')

    def access_create_button_tab_data(self, btn, smart_button=False, smart_button_string=False):
        """Create button and smart record inside new model"""
        # string_value is used in case of kanban view button store,
        string_value = 'string_value' in self._context.keys() and self._context['string_value'] or False
        button_type = 'type' in self._context.keys() and self._context['type'] or False
        try:
            name = btn.get('string') or string_value
            if smart_button:
                name = smart_button_string
            self.env['button.tab.data'].sudo().create({
                'access_model_id': self.access_model_id.id,
                'access_type': button_type or 'button',
                'access_name': btn.get('name'),
                'access_tab_button_string': name,
                'access_button_type': btn.get('type'),
                'access_is_smart_button': smart_button,
            })
        except Exception as e:
            raise ValidationError(e)
        # self.env.cr.commit()

    def access_create_smart_button_string(self, button_list, type=False):
        """ It will create smart button string"""

        def access_get_span_text(span_list):
            name = ''
            for sp in span_list:
                if sp.text:
                    name = name + ' ' + sp.text
            name = name.strip()
            return name

        for btn in button_list:
            name = ''
            field_list = btn.findall('field')
            if field_list:
                name = field_list[0].get('string')
            else:
                span_list = btn.findall('span')
                if span_list:
                    name = access_get_span_text(span_list)
                else:
                    div_list = btn.findall('div')
                    if div_list:
                        span_list = div_list[0].findall('span')
                        if span_list:
                            name = access_get_span_text(span_list)
            if not name:
                try:
                    name = btn.get('string')
                except:
                    pass
            if name and (type == 'object' or type == 'action'):
                domain = [('access_button_type', '=', btn.get('type')), ('access_tab_button_string', '=', name),
                          ('access_model_id', '=', self.access_model_id.id), ('access_type', '=', 'button')]
                if type == 'object':
                    domain += [('access_name', '=', btn.get('name'))]
                if type == 'action':
                    domain += [('access_name', '=', btn.get('name'))]
                smart_button_id = self.env['button.tab.data'].sudo().search(domain)
                if not smart_button_id:
                    self.access_create_button_tab_data(button_list, smart_button=True, smart_button_string=name)
                else:
                    smart_button_id[0].access_is_smart_button = True

    def access_get_string(self, btn, res, type):
        try:
            soup = BeautifulSoup(res['arch'], 'html.parser')
            buttons = soup.find_all(type, type=btn.get('type'))
            for button in buttons:
                if button.attrs.get('name') == btn.get('name'):
                    string_val = button.string or button.text if button.text else ''
                    string = string_val.replace('\n', '').strip()
                    if string:
                        return string
        except:
            return ''

    @api.onchange('access_model_id')
    def onchange_model_id(self):
        """On choosing model, drop down the related button"""
        if self.access_model_id and self.access_model_name:
            button_tab_object = self.env['button.tab.data'].sudo()
            view_object = self.env['ir.ui.view']
            view_list = ['form', 'tree', 'kanban']
            for view in view_list:
                for views in view_object.sudo().search(
                        [('model', '=', self.access_model_name), ('type', '=', view), ('inherit_id', '=', False)]):
                    res = self.env[self.access_model_name].sudo().get_view(view_id=views.id, view_type=view)
                    doc = etree.XML(res['arch'])

                    object_button = doc.xpath("//button[@type='object']")
                    for btn in object_button:
                        string_value = btn.get('string')
                        normal_button = True
                        if not string_value:
                            string_value = self.access_get_string(btn, res, type='button')
                        if btn.get('name') and string_value:
                            domain = [('access_button_type', '=', btn.get('type')),
                                      ('access_tab_button_string', '=', string_value),
                                      ('access_name', '=', btn.get('name')), ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'button')]
                            button_present = button_tab_object.sudo().search(domain)
                            if not button_present:
                                normal_button = False
                                self.with_context(string_value=string_value).access_create_button_tab_data(btn)
                            if not button_present and normal_button and btn.get('class') == 'oe_stat_button':
                                self.access_create_smart_button_string(btn, type=btn.get('type'))

                    action_button = doc.xpath("//button[@type='action']")
                    for btn in action_button:
                        string_value = btn.get('string')
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text if not btn.text.startswith('\n') else False
                            except:
                                pass
                            if not string_value:
                                string_value = self.access_get_string(btn, res, type='button')
                        if btn.get('name') and string_value:
                            domain = [('access_button_type', '=', btn.get('type')),
                                      ('access_tab_button_string', '=', string_value),
                                      ('access_name', '=', btn.get('name')), ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'button')]
                            if not button_tab_object.sudo().search(domain):
                                self.with_context(string_value=string_value).access_create_button_tab_data(btn)
                    kanban_object_button = doc.xpath("//a[@type='object']")
                    for btn in kanban_object_button:
                        string_value = btn.text
                        normal_button = True
                        if btn.get('name') and string_value and not string_value.startswith('\n'):
                            domain = [('access_button_type', '=', btn.get('type')),
                                      ('access_tab_button_string', '=', string_value),
                                      ('access_name', '=', btn.get('name')), ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'link')]
                            if not button_tab_object.sudo().search(domain):
                                self.with_context(string_value=string_value, type='link').access_create_button_tab_data(btn)
                            if normal_button and btn.get('class') == 'oe_stat_button':
                                self.access_create_smart_button_string(btn, type=btn.get('type'))

                    kanban_action_button = doc.xpath("//a[@type='action']")
                    for btn in kanban_action_button:
                        string_value = btn.get('string')
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text.strip() if not btn.text.startswith('\n') else False
                            except:
                                pass
                        if not string_value:
                            string_value = self.access_get_string(btn, res, type='a')
                        if btn.get('name') and string_value:
                            domain = [('access_button_type', '=', btn.get('type')),
                                      ('access_tab_button_string', '=', string_value),
                                      ('access_name', '=', btn.get('name')), ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'link')]
                            if not button_tab_object.sudo().search(domain):
                                self.with_context(string_value=string_value, type='link').access_create_button_tab_data(btn)
                    kanban_set_cover_button = doc.xpath("//a[@type='set_cover']")
                    for btn in kanban_set_cover_button:
                        string_value = btn.get('string')
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text if not btn.text.startswith('\n') else False
                            except:
                                pass
                        if not string_value:
                            string_value = self.access_get_string(btn, res, type='a')
                        if string_value:
                            domain = [('access_tab_button_string', '=', string_value),
                                      ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'link')]
                            if not button_tab_object.sudo().search(domain):
                                self.with_context(string_value=string_value, type='link').access_create_button_tab_data(btn)
                    kanban_edit_button = doc.xpath("//a[@type='edit']")
                    for btn in kanban_edit_button:
                        string_value = btn.get('string')
                        if view == 'kanban' and not string_value:
                            try:
                                string_value = btn.text if not btn.text.startswith('\n') else False
                            except:
                                pass
                        if string_value:
                            domain = [('access_button_type', '=', btn.get('type')),
                                      ('access_tab_button_string', '=', string_value),
                                      ('access_model_id', '=', self.access_model_id.id),
                                      ('access_type', '=', 'link')]
                            if not button_tab_object.sudo().search(domain):
                                self.with_context(string_value=string_value, type='link').access_create_button_tab_data(btn)

                    # Search pages for the selected model and create a record for it
                    page_list = doc.xpath("//page")
                    if page_list:
                        for page in page_list:
                            if page.get('string'):
                                domain = [('access_tab_button_string', '=', page.get('string')),
                                          ('access_model_id', '=', self.access_model_id.id), ('access_type', '=', 'page')]
                                if page.get('name'):
                                    domain += [('access_name', '=', page.get('name'))]
                                tab_exist = button_tab_object.sudo().search(domain, limit=1)
                                if not tab_exist:
                                    button_tab_object.create({
                                        'access_model_id': self.access_model_id.id,
                                        'access_name': page.get('name'),
                                        'access_tab_button_string': page.get('string'),
                                        'access_type': 'page',
                                    })


class accessButtonTab(models.Model):
    _name = 'button.tab.data'
    _description = 'Store Button/Tab data'
    _rec_name = 'access_tab_button_string'

    access_model_id = fields.Many2one('ir.model', string='Model', index=True, ondelete='cascade', required=True)
    access_model_name = fields.Char(string='Model Name', related='access_model_id.model', readonly=True, store=True)
    access_type = fields.Selection([('button', 'Button'), ('page', 'Page'), ('link', 'Link')], string="Type",
                               required=True)
    access_name = fields.Char('Name')
    access_tab_button_string = fields.Char('Attribute String', required=True)

    access_button_type = fields.Selection(
        [('object', 'Object'), ('action', 'Action'), ('edit', 'Edit'), ('set_cover', 'Set Cover')],
        string="Button Type")
    access_is_smart_button = fields.Boolean('Smart Button')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.access_tab_button_string
            if rec.access_name:
                name = name + ' (' + rec.access_name + ')'
                if rec.access_is_smart_button and rec.access_type == 'button':
                    name = name + ' (Smart Button)'
            result.append((rec.id, name))
        return result
