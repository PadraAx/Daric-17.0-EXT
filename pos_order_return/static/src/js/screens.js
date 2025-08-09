/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { renderToString } from "@web/core/utils/render";
import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { MyMessagePopup, OrderReturnPopup } from "@pos_order_return/js/popups";
import { OrdersScreenWidget } from "@pos_orders/js/main";
import { useService } from "@web/core/utils/hooks";

patch(PartnerListScreen.prototype, {
    setup(){
        super.setup();
        var self = this;
        var current_order = self.pos.get_order();
        setTimeout(function(){
            if (current_order != null && current_order.is_return_order) self.back();
        },50);
    }
});

patch(PaymentScreen.prototype, {
    onMounted() {
        super.onMounted();
        var self = this;
        var current_order = self.pos.get_order();
        if(current_order && current_order.is_return_order && current_order.get_total_with_tax() < 0){
            $('.payment-screen h1').html('Refund');
            $('.button.cancel_refund_order').show();
            if(current_order.is_exchange_order){
                $('.button.cancel_refund_order').hide();
            }
        } else if(current_order && current_order.is_return_order && current_order.get_total_with_tax() > 0){
            $('.payment-screen h1').html('Payment');
            $('.button.cancel_refund_order').show();
            if(current_order.is_exchange_order){
                $('.button.cancel_refund_order').hide();
            }
        } else {
            $('.button.cancel_refund_order').hide();
        }
    },
    click_delete_return_order(event){
        var order = this.pos.get_order();
        this.deleteOrder(order)
    },
    async deleteOrder(order) {
        var self = this;
        const screen = order.get_screen_data();

        if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: 'Existing orderlines',
                body: `${order.name} has total amount of ${this.getTotal(order)}, are you sure you want delete this order?`,
            });
            if (!confirmed) return;
        }
        if (order) {
            self.pos.removeOrder(order);
            self.pos.add_new_order();
        }
        this.pos.showScreen('ProductScreen');
    },
    getTotal(order) {
        return this.env.utils.formatCurrency(order.get_total_with_tax());
    }
});

patch(ProductScreen.prototype, {
    onMounted(){
        super.onMounted()
        var self = this;
        var current_order = self.pos.get_order();
        if (current_order != null && current_order.is_return_order && !current_order.is_exchange_order) {
            $('.product').css("pointer-events", "none");
            $('.product').css("opacity", "0.4");
            $('.product-list-container').css("pointer-events", "none");
            $('.product-list-container').css("opacity", "0.4");
            $('.header-cell').css("pointer-events", "none");
            $('.header-cell').css("opacity", "0.4");
            $('#refund_order_notify').show();
            $('#cancel_refund_order').show();
            $('.numpad-backspace').css("pointer-events", "none");
            $('.numpad').addClass('return_order_button');
            $('.numpad button').addClass('return_order_button');
            $('.button.set-partner').addClass('return_order_button');
            $('#all_orders').addClass('return_order_button');
        } else if (current_order != null && current_order.is_return_order && current_order.is_exchange_order) {
            $('.button.set-partner').addClass('return_order_button');
            $('#all_orders').addClass('return_order_button');
            $('#cancel_refund_order').hide();
        } else {
            $('.product').css("pointer-events", "");
            $('.product').css("opacity", "");
            $('.product-list-container').css("pointer-events", "");
            $('.product-list-container').css("opacity", "");
            $('.header-cell').css("pointer-events", "");
            $('.header-cell').css("opacity", "");
            $('#refund_order_notify').hide();
            $('#cancel_refund_order').hide();
            $('.numpad-backspace').css("pointer-events", "");
            $('.numpad').removeClass('return_order_button');
            $('.numpad button').removeClass('return_order_button');
            $('.button.set-partner').removeClass('return_order_button');
            $('#all_orders').removeClass('return_order_button');
        }
    },
    click_cancel_refund_order(event){
        var order = this.pos.get_order();
        this.deleteOrder(order)
    },
    async deleteOrder(order) {
        var self = this;
        const screen = order.get_screen_data();
        if (['ProductScreen', 'PaymentScreen'].includes(screen.name) && order.get_orderlines().length > 0) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: 'Existing orderlines',
                body: `${order.name} has total amount of ${this.getTotal(order)}, are you sure you want delete this order?`,
            });
            if (!confirmed) return;
        }
        if (order) {
            self.pos.removeOrder(order);
            self.pos.add_new_order();
        }
        self.onMounted();
    },
    getTotal(order) {
        return this.env.utils.formatCurrency(order.get_total_with_tax());
    },
    onNumpadClick(buttonValue){
        var order = this.pos.get_order();
        if (!order.is_return_order || (order.is_exchange_order && order.selected_orderline && !order.selected_orderline.original_line_id)){
            super.onNumpadClick(buttonValue);
        }
    }
});

patch(OrdersScreenWidget.prototype, {
    setup(){
        super.setup();
        this.popup = useService("popup");
    },
    onMounted(){
        super.onMounted();
        var self = this;
        this.props.details_visible = false;
        this.props.selected_tr_element = null;

        setTimeout(function(){
            $('.wk-order-list-contents').on('click', '.wk-order-line', function(event) {
                if (!(event.target && event.target.nodeName == 'BUTTON')) {
                    self.line_select(event, $(this), parseInt($(this).data('id')));
                }
            });
            var contents = $('.order-details-contents');
            contents.empty();
            var parent = $('.wk_order_list').parent();
            parent.scrollTop(0);
        },150);
    },
    line_select(event, $line, id) {
        var self = this;
        var order = self.pos.db.order_by_id[id];

        $('.wk_order_list .lowlight').removeClass('lowlight');
        if ($line.hasClass('highlight')) {
            $line.removeClass('highlight');
            $line.addClass('lowlight');
            self.display_order_details('hide', order);
        } else {
            $('.wk_order_list .highlight').removeClass('highlight');
            $line.addClass('highlight');
            self.props.selected_tr_element = $line;
            var y = event.pageY - $line.parent().offset().top;
            self.display_order_details('show', order, y);
        }
    },
    display_order_details(visibility, order, clickpos){
        var self = this;
        var contents = $('.order-details-contents');
        var parent = $('.wk_order_list').parent();
        var scroll = parent.scrollTop();
        var height = contents.height();
        var orderlines = [];
        var statements = [];
        var payment_methods_used = [];

        if (visibility === 'show') {
            order.lines.forEach(function(line_id) {
                orderlines.push(self.pos.db.line_by_id[line_id]);
            });
            if(order && order.payment_ids){
                order.payment_ids.forEach(function(payment_id) {
                    var payment = self.pos.db.payment_by_id[payment_id];
                    statements.push(payment);
                    payment_methods_used.push(payment.journal_id[0]);
                });
            }
            contents.empty();
            contents.append($(renderToString('OrderDetails', {
                 widget: this, order: order, orderlines: orderlines, statements: statements, env:this.env 
            })));
            var new_height = contents.height();
            if (!this.props.details_visible) {
                if (clickpos < scroll + new_height + 20) {
                    parent.scrollTop(clickpos - 20);
                } else {
                    parent.scrollTop(parent.scrollTop() + new_height);
                }
            } else {
                parent.scrollTop(parent.scrollTop() - height + new_height);
            }
            this.props.details_visible = true;
            $("#close_order_details").on("click", function() {
                if($('.wk-order-line.highlight').is(":visible")){
                    $('.wk-order-line.highlight').removeClass('highlight');
                    $('.wk-order-line.highlight').addClass('lowlight');
                    self.props.details_visible = false;
                    self.display_order_details('hide', null);
                }
            });
            $("#wk_refund").on("click", function() {
                var message = '';
                var non_returnable_products = false;
                var original_orderlines = [];
                var allow_return = true;
                if (order.return_status == 'Fully-Returned') {
                    message = 'No items are left to return for this order!!'
                    allow_return = false;
                }
                var all_pos_orders = self.pos.orders || [];
                var return_order_exist = all_pos_orders.find(function(pos_order) {
                    return pos_order.return_order_id && pos_order.return_order_id === order.id;
                });

                if (return_order_exist) {
                    self.popup.add(MyMessagePopup, {
                        'title': 'Refund Already In Progress',
                        'body': "Refund order is already in progress. Please proceed with Order Reference " + return_order_exist.sequence_number,
                    });
                } else if (allow_return) {
                    order.lines.forEach(function(line_id) {
                        var line = self.pos.db.line_by_id[line_id];
                        var product = self.pos.db.get_product_by_id(line.product_id[0]);
                        if (product == null) {
                            non_returnable_products = true;
                            message = 'Some product(s) of this order are unavailable in Point Of Sale, do you wish to return other products?'
                        } else if (product.not_returnable) {
                            non_returnable_products = true;
                            message = 'This order contains some Non-Returnable products, do you wish to return other products?'
                        } else if (line.qty - line.line_qty_returned > 0) original_orderlines.push(line);
                    });
                    if (original_orderlines.length == 0) {
                        self.popup.add(MyMessagePopup, {
                            'title': 'Cannot Return This Order!!!',
                            'body': "There are no returnable products left for this order. Maybe the products are Non-Returnable or unavailable in Point Of Sale!!",
                        });
                    } else if (non_returnable_products) self.confirm_popup(message, original_orderlines, order, true);
                    else {
                        self.popup.add(OrderReturnPopup, {
                            'orderlines': original_orderlines,
                            'order': order,
                            'is_partial_return': false,
                        });
                    }
                } else {
                    self.popup.add(MyMessagePopup, {
                        'title': 'Warning!!!',
                        'body': message,
                    });
                }
            });
        }
        if (visibility === 'hide') {
            contents.empty();
            if (height > scroll) {
                contents.css({ height: height + 'px' });
                contents.animate({ height: 0 }, 400, function() {
                    contents.css({ height: '' });
                });
            } else {
                parent.scrollTop(parent.scrollTop() - height);
            }
            this.props.details_visible = false;
        }
    },
    async confirm_popup(message, original_orderlines, order, is_partial_return){
        var self = this;
        const { confirmed } = await self.popup.add(ConfirmPopup, {
            title: 'Warning !!!',
            body: message,
        });
        if (confirmed) {
            self.popup.add(OrderReturnPopup, {
                'orderlines': original_orderlines,
                'order': order,
                'is_partial_return': is_partial_return,
            });
        }
    },
});