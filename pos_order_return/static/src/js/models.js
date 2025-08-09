/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PosDB } from "@point_of_sale/app/store/db";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { roundPrecision as round_pr } from "@web/core/utils/numbers";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.db._loadPosPayment(loadedData['pos.payment']);
    },
    set_order(order, options){
        super.set_order(...arguments);
        if (order && (!order.is_return_order || order.is_exchange_order)) {
            $("#cancel_refund_order").hide();
        } else {
            $("#cancel_refund_order").show();
        }
    }
});

patch(PosDB.prototype, {
    _loadPosPayment: function(payments){
        var self = this;
        self.all_payments = payments;
        self.payment_by_id = {};

        payments.forEach(function(payment) {
            self.payment_by_id[payment.id] = payment;
            self.payment_by_id[payment.id]['journal_id'] = payment.payment_method_id;
            delete self.payment_by_id[payment.id]['payment_method_id'];
        });
    },
});

patch(Order.prototype, {
    setup(){
        super.setup(...arguments);
        this.return_status = '-';
        this.is_return_order = false;
        this.return_order_id = false;
    },
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        if (json.return_status){
            this.return_status = json.return_status
        }
        if (json.is_return_order){
            this.is_return_order = json.is_return_order
        }
        if (json.return_order_id){
            this.return_order_id = json.return_order_id
        }
    },
    get_due(paymentline) {
        var self = this;
        if (self.is_return_order && this.get_total_with_tax() < 0) {
            if (!paymentline) var due = (Math.abs(this.get_total_with_tax()) - this.get_total_paid());
            else {
                var due = Math.abs(this.get_total_with_tax());
                var lines = this.paymentlines;
                for (var i = 0; i < lines.length; i++) {
                    if (lines[i] === paymentline) break;
                    else due -= lines[i].get_amount();
                }
            }
            return round_pr(Math.max(0, due), this.pos.currency.rounding);
        } else return super.get_due(...arguments);
    },
    get_change(paymentline) {
        var self = this;
        if (self.is_return_order && self.get_total_with_tax() < 0) {
            if (!paymentline) {
                var change = this.get_total_paid() - Math.abs(this.get_total_with_tax());
            } else {
                var change = -Math.abs(this.get_total_with_tax());
                var lines = this.paymentlines;
                for (var i = 0; i < lines.length; i++) {
                    change += lines[i].get_amount();
                    if (lines[i] === paymentline) break;
                }
            }
            return round_pr(Math.max(0, change), this.pos.currency.rounding);
        } else return super.get_change(...arguments);
    },
    export_as_JSON(){
        var json = super.export_as_JSON(...arguments);
        var current_order = this;
        if (current_order != null) {
            json.is_return_order = current_order.is_return_order;
            json.return_status = current_order.return_status;
            json.return_order_id = current_order.return_order_id;
        }
        return json;
    },
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.is_return_order =  this.is_return_order;
        result.is_exchange_order =  this.is_exchange_order;
        return result;
    }
});

patch(Orderline.prototype, {
    setup(){
        super.setup(...arguments);
        this.line_qty_returned = 0;
        this.original_line_id = null;
    },
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        if (json.line_qty_returned){
            this.line_qty_returned = json.line_qty_returned
        }
        if (json.original_line_id){
            this.original_line_id = json.original_line_id
        }
    },
    export_as_JSON(){
        var json = super.export_as_JSON(...arguments);
        var current_line = this;
        if (current_line) {
            json.line_qty_returned = current_line.line_qty_returned;
            json.original_line_id = current_line.original_line_id;
        }
        return json;
    },
    can_be_merged_with(orderline){
        var current_order = this.pos.get_order();
        if (current_order && current_order.is_return_order && this.quantity < 0){
            return false;
        } else return super.can_be_merged_with(...arguments);
    }
});

patch(Payment.prototype, {
    set_amount(value){
        var self = this;
        super.set_amount(...arguments);
        var order = self.pos.get_order()
        var change = order.get_change();
        var buffer_amount = parseFloat(value);
        if (order.is_return_order && change > 0 && order.get_total_with_tax() < 0) {
            var amount = (buffer_amount - change);
            this.amount = amount
        }
    }
});