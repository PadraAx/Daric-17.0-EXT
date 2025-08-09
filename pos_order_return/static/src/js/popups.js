/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class MyMessagePopup extends AbstractAwaitablePopup {
    static template = "MyMessagePopup";
    static defaultProps = {
        title: 'Message', value:''
    };
};

export class OrderReturnPopup extends AbstractAwaitablePopup {
    static template = "OrderReturnPopup";
    static defaultProps = {
        title: 'Message', value:''
    };

    setup(){
        super.setup();
        this.pos = usePos();
    }

    click_return_order(event){
        var self = this;
        var all = $('.return_qty');
        var return_dict = {};
        var return_entries_ok = true;
        
        $.each(all, function(index, value) {
            var input_element = $(value).find('input');
            var line_quantity_remaining = parseFloat(input_element.attr('line-qty-remaining'));
            var line_id = parseFloat(input_element.attr('line-id'));
            var qty_input = parseFloat(input_element.val());
            if (!$.isNumeric(qty_input) || qty_input > line_quantity_remaining || qty_input < 0) {
                return_entries_ok = false;
                input_element.css("background-color", "#ff8888;");
                setTimeout(function() {
                    input_element.css("background-color", "");
                }, 100);
                setTimeout(function() {
                    input_element.css("background-color", "#ff8888;");
                }, 200);
                setTimeout(function() {
                    input_element.css("background-color", "");
                }, 300);
                setTimeout(function() {
                    input_element.css("background-color", "#ff8888;");
                }, 400);
                setTimeout(function() {
                    input_element.css("background-color", "");
                }, 500);
            }

            if (qty_input == 0 && line_quantity_remaining != 0 && !self.props.is_partial_return){
                self.props.is_partial_return = true;
            } else if (qty_input > 0) {
                return_dict[line_id] = qty_input;
                if (line_quantity_remaining != qty_input && !self.props.is_partial_return)
                    self.props.is_partial_return = true;
                else if (!self.props.is_partial_return)
                    self.props.is_partial_return = false;
            }            
        });
        if (return_entries_ok) self.create_return_order(return_dict);
    }
    create_return_order(return_dict){
        var self = this;
        var order = self.props.order;
        
        if (Object.keys(return_dict).length > 0) {
            var refund_order = self.pos.get_order();
            if(refund_order && (refund_order.is_return_order || refund_order.is_exchange_order)){
                self.pos.add_new_order()
                refund_order = self.pos.get_order();
            }
            this.cancel();
            refund_order.is_return_order = true;
            refund_order.set_partner(self.pos.db.get_partner_by_id(order.partner_id[0]));
            Object.keys(return_dict).forEach(function(line_id) {
                var line = self.pos.db.line_by_id[line_id];
                var product = self.pos.db.get_product_by_id(line.product_id[0]);
                refund_order.add_product(product, { quantity: -1 * parseFloat(return_dict[line_id]), price: line.price_unit, discount: line.discount });
                refund_order.selected_orderline.original_line_id = line.id;
            });
            if (self.props.is_partial_return) {
                refund_order.return_status = 'Partially-Returned';
                refund_order.return_order_id = order.id;
            } else {
                refund_order.return_status = 'Fully-Returned';
                refund_order.return_order_id = order.id;
            }
            self.props.resolve({ confirmed: false, payload: false });
            self.pos.closeTempScreen();
            self.pos.showScreen('PaymentScreen');
        } else {
            $(".popup input").css("background-color", "#ff8888;");
            setTimeout(function() {
                $(".popup input").css("background-color", "");
            }, 100);
            setTimeout(function() {
                $(".popup input").css("background-color", "#ff8888;");
            }, 200);
            setTimeout(function() {
                $(".popup input").css("background-color", "");
            }, 300);
            setTimeout(function() {
                $(".popup input").css("background-color", "#ff8888;");
            }, 400);
            setTimeout(function() {
                $(".popup input").css("background-color", "");
            }, 500);
        }
    }
    click_complete_return(event){
        var all = $('.return_qty');
        $.each(all, function(index, value) {
            var line_quantity_remaining = parseFloat($(value).find('input').attr('line-qty-remaining'));
            $(value).find('input').val(line_quantity_remaining);
        });
    }
}