// /** @odoo-module **/
// odoo.define('asset.confirm_before_submit', function (require) {
//     "use strict";

//     var FormController = require('web.FormController');
//     var core = require('web.core');
//     var _t = core._t;

//     FormController.include({
//         renderButtons: function () {
//             this._super.apply(this, arguments);

//             var self = this;
//             this.$buttons.find('.o_form_button_save').click(function () {
//                 self.confirmBeforeSubmit();
//             });
//         },

//         confirmBeforeSubmit: function () {
//             var self = this;

//             var dialog = new Dialog(self, {
//                 title: _t("Confirmation"),
//                 size: 'medium',
//                 $content: $('<div>').text(_t("Are you sure you want to perform this action?")),
//                 buttons: [
//                     {
//                         text: _t("Cancel"),
//                         close: true,
//                     },
//                     {
//                         text: _t("Confirm"),
//                         classes: 'btn-primary',
//                         click: function () {
//                             // Perform the action if confirmed
//                             self.trigger_up('button_clicked', {id: self.view.datarecord.id});
//                             dialog.close();
//                         },
//                     },
//                 ],
//             });

//             dialog.open();
//         },
//     });
// });