odoo.define('geo_address.postal_code_rules', [
    'web.ListRenderer',
    'web.relational_fields',
    'web.field_registry',
], function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var FieldRegistry = require('web.field_registry');

    ListRenderer.include({
        _renderView: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.$el.parents('.postal_code_settings_section').length) {
                    self.$('.o_list_table').css({
                        'min-width': '800px',
                        'width': '100%'
                    });
                    self.$el.css('overflow-x', 'auto');
                }
                return self;
            });
        },
    });

    var PostalCodeRulesWidget = FieldOne2Many.extend({
        _render: function () {
            return this._super.apply(this, arguments).then(function () {
                this.$('.o_list_view').css('min-width', '800px');
            });
        },
    });

    FieldRegistry.add('postal_code_rules_widget', PostalCodeRulesWidget);
});
