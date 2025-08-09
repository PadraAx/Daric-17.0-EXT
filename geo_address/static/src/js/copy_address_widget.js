// Corrected copy_address_widget.js
odoo.define('geo_address.copy_address_widget', ['web.core', 'web.basic_fields', 'web.field_registry'], function (require) {
    "use strict";

    var core = require('web.core');
    var FieldChar = require('web.basic_fields').FieldChar;
    var fieldRegistry = require('web.field_registry');
    var _t = core._t;

    var CopyAddressWidget = FieldChar.extend({
        className: 'o_field_copy_address',
        supportedFieldTypes: ['char', 'text'],
        events: {
            'click .o_copy_icon': '_onClickCopy',
        },

        _renderReadonly: function () {
            this._super.apply(this, arguments);
            if (this.value) {
                this.$el.append($('<span>', {
                    class: 'fa fa-copy o_copy_icon ml-2',
                    title: _t('Copy to clipboard'),
                    css: {
                        cursor: 'pointer',
                        color: '#7C7BAD',
                        'margin-left': '5px'
                    }
                }));
            }
        },

        _onClickCopy: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();

            if (!this.value) return;

            var self = this;
            navigator.clipboard.writeText(this.value).then(function () {
                self.displayNotification({
                    title: _t('Success'),
                    message: _t('Text copied to clipboard'),
                    type: 'success',
                    sticky: false
                });
            }).catch(function (err) {
                self.displayNotification({
                    title: _t('Error'),
                    message: _t('Failed to copy text'),
                    type: 'danger',
                    sticky: false
                });
                console.error('Copy failed:', err);
            });
        }
    });

    fieldRegistry.add('copy_address', CopyAddressWidget);

    return CopyAddressWidget;
});