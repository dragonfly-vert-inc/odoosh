odoo.define('mrp_plm_upgrade_mo.eco_bom_change_report', function (require) {
'use strict';

var core = require('web.core');
var mrp_bom_report = require('mrp.mrp_bom_report');
var session = require('web.session');

var EcoBomChange = mrp_bom_report.extend({
    get_html: function() {
        var self = this;
        var args = [
            false,
            this.given_context.searchQty || 1,
            this.given_context.searchVariant,
        ];
        return this._rpc({
                model: 'report.mrp.report_eco_changes',
                method: 'get_html',
                args: args,
                context: this.given_context,
            })
            .then(function (result) {
                self.data = result;
            });
    },
    get_bom: function(event) {
        var self = this;
        var $parent = $(event.currentTarget).closest('tr');
        var activeID = $parent.data('id');
        var productID = $parent.data('product_id');
        var lineID = $parent.data('line');
        var qty = $parent.data('qty');
        var level = $parent.data('level') || 0;
        return this._rpc({
                model: 'report.mrp.report_eco_changes',
                method: 'get_bom',
                args: [
                    activeID,
                    productID,
                    parseFloat(qty),
                    lineID,
                    level + 1,
                ],
                context: this.given_context,
            })
            .then(function (result) {
                self.render_html(event, $parent, result);
            });
      },
});

core.action_registry.add('eco_bom_changes', EcoBomChange);
return EcoBomChange;
});