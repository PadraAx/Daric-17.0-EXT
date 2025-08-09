# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo.http import route, request, Controller, Response
from odoo.addons.portal.controllers.portal import CustomerPortal
import werkzeug
import json
import logging
from odoo.exceptions import ValidationError
_log = logging.getLogger(__name__)
MAX_PAGE_SIZE_PAGINATION = 10


class QuickSearchConroller(Controller):

###########################################################
## Change currency according as from_currency to to_currency
############################################################
    def compute_currency(self, price):
        order = request.website.sale_get_order(force_create=1)
        from_currency = order.company_id.currency_id
        to_currency = order.pricelist_id.currency_id
        return round(from_currency.compute(price, to_currency), 2)


    def variants_availability(self):
        website = (request.env['website'].get_current_website()).id
        quick_order = request.env['quick.order'].search([('state','=','draft'), ('user_id', '=', request.uid),('website_id', '=', website)])
        return [id.product_id.id for id in quick_order.quick_order_line]

    #****************************************************************************************************************
    ## here we will check that draft quick order has any unpublished product
    ## Case 1: If yes then check total products count if 1 product available then we will remove that with msg
    ## Case 2: count more then 1 then only remove product not show any msg
    #****************************************************************************************************************
    def _remove_unpublished_quick_order_line(self,quick_orders):
        warning = False
        for quick_order in quick_orders:
            order_line_with_unpublished_product = quick_order.sudo().quick_order_line.filtered(lambda r: r if r.product_id.product_tmpl_id.sudo().is_published is not True else None)
            len_of_order_line = len(quick_order.quick_order_line)
            if order_line_with_unpublished_product:
                quick_order.sudo().write({'quick_order_line': [(2, rec.id, False) for rec in order_line_with_unpublished_product]})
                if len_of_order_line == 1:
                    warning = "warning"
        return warning
            # quick_order.write({'quick_order_line': [(2, rec.id, False) for rec in quick_order.sudo().quick_order_line.filtered(lambda r: r if r.product_id.product_tmpl_id.is_published is not True else None)]})

    def shopping_list_availability(self, shopping_list):
        if len(shopping_list)==1:
            return [id.product_id.id for id in shopping_list.quick_order_line]
        return []
###########################################################################
## Get main page, product Order List, searching logic, pagination and
## domain filter for product template that are already in Order List.
###########################################################################
    @route(['/quickorder','/quickorder/page/<page_no>','/quickorder/quicksearch'], type = 'http', auth = 'public', website = True)
    def get_quick_search_form(self,search='', page_no=1, key_press=False, **kw):
        if request.website.is_public_user():
            return request.render('quick_order.quick_order_public_user_sugges',{})
        # _logger.info("===================request=========%s"%request.)
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            order_quick = request.env["quick.order"].search([('user_id', '=', request.uid), ('website_id', '=', website), ('state', '=', 'draft')])
            unpublished_order_line = self._remove_unpublished_quick_order_line(order_quick)
            domain = [('product_variant_ids.id', 'not in', self.variants_availability()),('website_published','=', True)]
            error = ''
            s_error = ''
            prev_str = request.session.get('previous_search_string')
            not_click_event = request.httprequest.full_path.startswith('/quickorder/quicksearch')
            if not (prev_str == search) and not not_click_event:
                if search:
                    url = '/quickorder?search='+search
                else:
                    url = '/quickorder'
                request.session['previous_search_string'] = search
                return werkzeug.utils.redirect(url)
            if search:
                for srch in search.split(" "):
                    domain += [
                                '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                                ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)
                            ]
            page_no = int(page_no)
            offset = (page_no-1)*MAX_PAGE_SIZE_PAGINATION
            prod = request.env['product.template'].search(domain)
            if len(prod) <= 0:
                s_error = request.env['quick.order.message'].search([('website_id', '=', website)],limit=1)
                s_error = s_error.message_on_product_search
            length = len(prod)//MAX_PAGE_SIZE_PAGINATION
            if len(prod)%MAX_PAGE_SIZE_PAGINATION == 0:
                length = length
            else:
                length = length+1
            pager = request.website.pager(url="/quickorder", total=len(prod), page=page_no, step=MAX_PAGE_SIZE_PAGINATION, scope=5, url_args={"search": search})
            if len(order_quick.quick_order_line) <= 0:
                error = request.env['quick.order.message'].search([('website_id', '=', website)],limit=1)
                error = error.message_on_empty_order_list
            shopping_list = request.env["quick.order"].search([('user_id', '=', request.uid), ('website_id', '=', website), ('state', '=', 'shopping_list')])
            response = {
                'products' : prod[offset : offset+MAX_PAGE_SIZE_PAGINATION],
                'search_count' : len(prod),
                'pager' : pager,
                'order_quicks' : order_quick.quick_order_line,
                'id' : order_quick.id,
                'shopping_list' : shopping_list,
                'error' : {'error': error, 's_error': s_error},
                'compute_currency' : self.compute_currency,
                'product_r': self.variants_availability(),
                'warning': True if unpublished_order_line else False
                }
            if not not_click_event:
                request.session['previous_search_string'] = search
            if search:
                response['search']=search
            if key_press:
                return request.render('quick_order.main_table_data', response)
            return request.render('quick_order.quick_search_main_template', response)
        return request.redirect('/shop')

###################################################################################
## Get the all variants of product template if exixts else submit into Order List
###################################################################################
    @route(['/quickorder/getvariants'], type = "http", auth = "user", website = True)
    def get_variants(self, product_id, **kw):
        product_id = int(product_id)
        products = None
        total_valid =[]
        prod = request.env['product.template'].sudo().browse(product_id)
        not_id = prod.product_variant_ids.ids
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            user_exists = request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'draft'),('website_id', '=', website)])
            if len(prod.product_variant_ids) == 1:
                if user_exists:
                    products_exists = self.variants_availability()
                    if prod.product_variant_ids.id not in products_exists:
                        user_exists.quick_order_line = [(0, 0, {"product_id" : prod.product_variant_ids.id})]
                elif not user_exists:
                    user_exists = request.env['quick.order'].create({
                                                "quick_order_line": [(0, 0, {"product_id" : prod.product_variant_ids.id})],
                                                "website_id": website,
                                                })
                products = prod.product_variant_ids.ids
                return Response(request.env['ir.qweb']._render('quick_order.add_to_cart_mutliple_body',{'order_quicks' : user_exists.quick_order_line, 'id':user_exists.id, 'compute_currency' : self.compute_currency, 'product_r': products}),content_type='text/html;charset=utf-8',status=211)
            if not prod.product_variant_ids:
                return Response({'error' : "No variants found"}, content_type='application/json',status=500)
            if user_exists:
                not_id = list(set(prod.product_variant_ids.filtered(lambda x: x.product_tmpl_id._is_combination_possible(x.product_template_attribute_value_ids)).ids)-set(self.variants_availability()))
            return request.render("quick_order.row_select_model", {"docs" : prod, "not_id" : not_id})
        return request.redirect('/shop')


##########################################################################
## Submit the variants of product template into Quick Order List
##########################################################################
    @route(['/quickorder/addproducts'], methods=['POST'], type = "json", auth = "user", website = True)
    def add_products(self, **kw):
        product_ids = kw.get('product_ids')
        products = None
        total_valid = []
        delete_template_row = False
        template = ''
        product_r = []
        website = (request.env['website'].get_current_website()).id
        try :
            if len(product_ids):
                user_exists = request.env['quick.order'].sudo().search([('user_id', '=', request.uid),('website_id', '=', website),('state', '=', 'draft')])
                if user_exists:
                    products_exists = self.variants_availability()
                    for product_id in product_ids:
                        if int(product_id) not in products_exists:
                            user_exists.quick_order_line= [(0,0,{"product_id" : int(product_id), "description" : product_ids[product_id]})]
                            total_valid.append(int(product_id))
                    product_r = total_valid
                elif not user_exists:
                    for product_id in product_ids:
                        ids = [(0,0, {"product_id" : int(id),"description" : product_ids[id]}) for id in product_ids]
                    product_r = [int(id) for id in product_ids]
                    user_exists = request.env['quick.order'].sudo().create({
                        'quick_order_line': ids,
                        'website_id': website,
                    })
                    products = user_exists.quick_order_line
                user_exists = request.env['quick.order'].sudo().search([('user_id', '=', request.uid),('state', '=', 'draft'),('website_id', '=', website)])
                if total_valid:
                    products = user_exists.quick_order_line
                if products:
                    template = request.env['ir.qweb']._render('quick_order.add_to_cart_mutliple_body',{'order_quicks' : products,'id' :user_exists.id, 'compute_currency' : self.compute_currency, 'product_r':  product_r})
                product_template = request.env['product.template'].search([('product_variant_ids.id', '=', int(list(product_ids.keys())[0]))])
                if product_template:
                    combination = set(product_template.product_variant_ids.filtered(lambda x: x.product_tmpl_id._is_combination_possible(x.product_template_attribute_value_ids)).ids)
                    delete_template_row = (set(self.variants_availability()) > combination) or (set(self.variants_availability()) == combination)
                return {
                    "template" : template,
                    "delete_template_row" : delete_template_row
                    }
        except Exception as e:
            raise ValidationError('Product id is invalid need int found String {}.'.format(e))
        return Response({'error' : "error"}, content_type='application/json',status=500)

########################################################################
## Delete the products from Quick Order List baesd on product id
########################################################################
    @route(['/quickorder/deleteproduct'], type = "json", auth = "user", website = True)
    def delete_product(self, item_id='', **kw):
        success = ''
        delete = False
        website = (request.env['website'].get_current_website()).id
        if item_id:
            user_exists = request.env['quick.order'].search([('user_id', '=', request.uid),('state','=', 'draft'),('website_id', '=', website)])
            if user_exists:
                user_exists.write({"quick_order_line":[(2, int(item_id))]})
                if not len(user_exists.quick_order_line):
                    success  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
                    success = success.message_on_delete_all_products
                    delete = True
        return {"success" : success, "delete" : delete}

#####################################################################################
## Delete the all products from Quick Order List baesd on product id accepted as json
#####################################################################################
    @route(['/quickorder/deleteallproduct'], type = "json", auth = "user", website = True)
    def delete_all_product(self, **kw):
        website = (request.env['website'].get_current_website()).id
        user_exists = request.env['quick.order'].search([('user_id', '=', request.uid),('state','=', 'draft'),('website_id', '=', website)])
        if user_exists.quick_order_line:
            ids = [(2, id) for id in user_exists.quick_order_line.ids]
            user_exists.write({'quick_order_line':ids})
        success  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        return {"success" : success.message_on_delete_all_products}

################################################################################################
## Move Quick Order List into Order Cart as a single entity and change state of Quick Order List
################################################################################################
    @route(['/quickorder/createorder'], auth="user", type="json", website=True)
    def create_order(self,id=0, order_now=[], **kw):
        website = (request.env['website'].get_current_website()).id
        success  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        try :
            quick_order = request.env['quick.order'].browse(int(id))
        except Exception as e:
            raise ValidationError('Product id is invalid need int found String {}.'.format(e))
        if order_now and quick_order.state != 'done':
            total_lines = []
            sale_order = request.website.sale_get_order(force_create=1)
            if sale_order.order_line:
                total_lines = [order.product_id.id for order in sale_order.order_line]
            for order in order_now:
                if order.get('id') not in total_lines:
                        sale_order._cart_update(
                            product_id = order['id'],
                            line_id = None, 
                            set_qty = order.get('quantity'),
                            product_custom_attribute_values = order['variant_custom_values'] if order['variant_custom_values'] else False,
                            add_qty = None)
                else:
                    order_line = request.env['sale.order.line'].sudo().search([('product_id', '=', order['id'])])
                    if len(order_line) > 0:
                        sale_order._cart_update(
                            product_id = order.get('id'), 
                            line_id = order_line[0].id, 
                            add_qty = order.get('quantity'), 
                            product_custom_attribute_values = order['variant_custom_values'] if order['variant_custom_values'] else False, 
                            set_qty = None )
            if not id:
                user_exists = request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'draft'),('website_id', '=', website)])
            if id:
                user_exists = request.env['quick.order'].browse(int(id))
            user_exists.write({'state' : 'done'})
            return success.message_on_empty_order_list
        return {"error": success.empty_shopping_list_submit}

######################################################################################
## Move Quick Order List into Shopping List by changing the state of Quick Order List
######################################################################################
    @route(['/quickorder/addshoppinglist'], auth='user', type='json', website=True)
    def add_shopping_list(self, name='', id=None, create=False, list_id= 0, **kw):
        quick_order = request.env['quick.order'].browse(int(id))
        quick_order.write({"state": "done"})
        product_ids = []
        template = ''
        data = {}
        if id and create:
            if quick_order:
                quick_order.write({"name": name, "state": "shopping_list"})
                return {
                        "url" : "/quickorder/shoppinglist/"+str(quick_order.id),
                        "route" : True
                    }
        elif id and list_id:

            quick_order_1 = request.env['quick.order'].browse(int(list_id))
            products = self.shopping_list_availability(quick_order_1)
            for id in quick_order.quick_order_line:
                if id.product_id.id not in products:
                    product_ids.append((4,id.id))
                else:
                    q_products = quick_order_1.quick_order_line.filtered(lambda x: x.product_id.id == id.product_id.id)
                    if q_products.exists():
                        q_products.quantity = id.quantity + q_products.quantity
            if product_ids:
                quick_order_1.write({"quick_order_line": product_ids})
                quick_order.unlink()
            return {
                    "url" : "/quickorder/shoppinglist/"+str(quick_order_1.id),
                    "route" : True
                }
        return json.dumps({"route" : False})

##################################################################
## Get All Shopping List and also based on id
##################################################################
    @route(['/quickorder/shoppinglist', '/quickorder/shoppinglist/<int:shopping_id>'], auth='user', type='http', website=True)
    def shopping_list(self,shopping_id=0, id=0, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            shopping_lists = request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'shopping_list'),('website_id', '=', website)])
            unpublished_order_line = self._remove_unpublished_quick_order_line(shopping_lists)
            if id:
                shopping_list = request.env['quick.order'].search([('id', '=', int(id)),('state', '=', 'shopping_list'),('user_id', '=', request.uid),('website_id', '=', website)])
                return request.env['ir.qweb']._render('quick_order.add_to_cart_mutliple',{
                                                                        'shopping_lists' : shopping_list,
                                                                        'shopping_list' : shopping_lists,
                                                                        'compute_currency' : self.compute_currency,
                                                                        'product_r': self.shopping_list_availability(shopping_list)
                                                                        })
            if shopping_id:
                shopping_list = request.env['quick.order'].search([('id', '=', shopping_id), ('state', '=', 'shopping_list'),('user_id', '=', request.uid),('website_id', '=', website)])
                try:
                    len(shopping_list.quick_order_line)
                except Exception:
                    shopping_list=None
            else:
                shopping_list = request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'shopping_list'),('website_id', '=', website)])
            s_error = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
            return request.render('quick_order.shopping_list', {
                            'shopping_lists' : shopping_list,
                            'shopping_list' : shopping_lists,
                            'compute_currency' : self.compute_currency,
                            'error' :{'s_error': s_error.message_on_empty_shopping_list},
                            'warning': True if unpublished_order_line else False,
                            'product_r': self.shopping_list_availability(shopping_list)
                        })
        return request.redirect('/shop')

####################################################################
## Delete all Shopping Lists and also baesd on unique id.
####################################################################
    @route(['/quickorder/shoppinglist/delete'], auth='user', type='http', website=True)
    def shopping_list_delete(self, shopping_id=0, product_id=0, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            if shopping_id:
                shopping_list = request.env['quick.order'].search([('id', '=', int(shopping_id)),('state', '=', 'shopping_list'), ('website_id', '=', website), ('user_id', '=', request.uid)])
                if shopping_list:
                    if int(product_id) in shopping_list.quick_order_line.ids:
                        shopping_list.write({"quick_order_line": [(2, int(product_id))]})
                    elif not product_id:
                        shopping_list.unlink()
                        if len(request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'shopping_list'),('website_id', '=', website)])) <= 0:
                            s_error = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
                            return request.env['ir.qweb']._render('quick_order.404',{'error' :{'s_error': s_error.message_on_empty_shopping_list}})
                    return json.dumps({'success' : "success"})
            return json.dumps({'error' : "error"})
        return request.redirect('/shop')

############################################################################
## Move Shopping List into Order Cart and chnge the state of Shopping List.
############################################################################
    @route(['/quickorder/shoppinglist/curd'], auth='user', type='json', website=True)
    def shopping_list_curd(self, shopping_id, order_now = [] , **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order = request.env['quick.order'].search([('id', '=', int(shopping_id)),('website_id', '=', website),('state', '=', 'shopping_list'), ('user_id', '=', request.uid)])
        if not order_now:
            order_now = [{'id': order.product_id.id, 'quantity': order.quantity} for order in quick_order.quick_order_line]
        if quick_order:
            return self.create_order(shopping_id,order_now)
        s_error = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        return {"error": s_error.empty_shopping_list_submit}

    @route(['/my/quickorder'], auth='user', type='http', website=True)
    def my_quick_orders(self, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            total_quick_order = request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'done'),('website_id', '=', website)])
            return request.render('quick_order.portal_my_quick_order',{'quick_orders':total_quick_order,'page_name':'quick_order'})
        return request.redirect('/shop')

    @route(['/my/quickorder/<int:id>'], auth='user', type='http', website=True)
    def my_quick_orders_products(self, id=0, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            value = {}
            if id:
                total_quick_order = request.env['quick.order'].search([('id','=',id),('website_id','=',website)])
                if request.website.sudo().user_id.share:
                    total_quick_order.sudo().quick_order_line.filtered(lambda _: _.product_id.is_published is False).unlink()
                value = {
                    "name": total_quick_order.name,
                    "quick_order": total_quick_order.sudo().quick_order_line,
                    "compute_currency": self.compute_currency,
                    "page_name": "quick_products"
                    }
            return request.render('quick_order.portal_my_quick_order_details',value)
        return request.redirect('/shop')

    @route(['/my/quickorder/update'], auth='user', type='http', website=True)
    def quick_order_recover_shopping_lists(self, id=0, action='', **kw):
        urls = '/quickorder'
        if id:
            try:
                id = int(id)
            except Exception:
                return request.redirect(urls)
            total_quick_order = request.env['quick.order'].browse(id)
            if action == 're-order':
                sale_order = request.website.sale_get_order(force_create=1)
                for products in total_quick_order.sudo().quick_order_line.filtered(lambda x: x.product_id.website_published):
                    attr_ids = products.product_id.product_template_attribute_value_ids
                    custom_attr_ids = False
                    product_custom_attribute_values = []
                    if attr_ids.ids:
                        custom_attr_ids = (attr_ids.filtered(lambda attr_id: attr_id if attr_id.is_custom else None))
                    if custom_attr_ids:
                        for custom_attr_id in custom_attr_ids:
                            product_custom_attribute_values.append({
                                'custom_product_template_attribute_value_id': custom_attr_id.id,
                                'attribute_value_name': custom_attr_id.name,
                                'custom_value': products._get_custom_value(custom_attr_id.product_attribute_value_id.id)
                            })
                    sale_order._cart_update(
                        product_id = products.product_id.id,
                        line_id = None,
                        product_custom_attribute_values = product_custom_attribute_values, 
                        add_qty = products.quantity,)
                urls = '/shop/cart'
            elif action == 'shopping-list' :
                total_quick_order.write({'state': 'shopping_list'})
                unpublished_line = total_quick_order.sudo().quick_order_line.filtered(lambda x: not x.product_id.website_published)
                unpublished_line.unlink()
                urls = '/quickorder/shoppinglist/'+str(total_quick_order.id)
        return request.redirect(urls)

    @route(['/quickorder/update/name'], auth="public", website=True, type="json")
    def update_shopping_list_name(self, s_name='', id=0, **kw):
        success = "No"
        name = ""
        if id:
            try:
                quick_order = request.env['quick.order'].browse(int(id))
                quick_order.write({'name':s_name})
                success = "ok"
                name = quick_order.name+str('<span class="open-e-sp-name"><i class="fa fa-pencil-square-o" aria-hidden="true"></i></span>')
            except Exception:
                return {"success": "No"}
        return {"success": success, "name": name}

    @route(['/quickorder/shoppinglist/update/quantity'], auth="user", website="true", type="http")
    def update_quanity(self, line_id=0, qty=0, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            if line_id:
                quick_order = request.env['quick.order.line'].browse(int(line_id))
                quick_order.write({"quantity" : int(qty)})
                res = quick_order.product_id.product_tmpl_id._get_combination_info(product_id=quick_order.product_id.id, add_qty=quick_order.quantity)
            return json.dumps({"price" : res['price']})
        return request.redirect('/shop')

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            if 'total_quick_order_val' in counters:
                values['total_quick_order_val'] = request.env['quick.order'].search_count([('user_id', '=', request.uid),('state', '=', 'done'),('website_id','=', website)])
            return values
        return values

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        website = (request.env['website'].get_current_website()).id
        quick_order_config  = request.env['quick.order.message'].search([('website_id', '=', website)], limit = 1)
        if(quick_order_config):
            values = super(CustomerPortal, self).home(**kw)
            website = (request.env['website'].get_current_website()).id
            total_quick_order = len(request.env['quick.order'].search([('user_id', '=', request.uid),('state', '=', 'done'),('website_id','=', website)]).ids)
            values.qcontext.update({"total_quick_order":total_quick_order})
            return values
        return super(CustomerPortal, self).home(**kw)
