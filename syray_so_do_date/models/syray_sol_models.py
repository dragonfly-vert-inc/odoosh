# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil import relativedelta

class SPDModel(models.Model):
    _inherit = 'stock.move'

    date_expected_custom = fields.Datetime("Delivery Date")

class SOLModel(models.Model):
    _inherit = 'sale.order.line'

    #sol_delivery_date = fields.Datetime.from_string('Delivery Date Sol')
    date_expected = fields.Datetime('Delivery Date')

    sol_priority = fields.Selection([
        ('1', 'Low'), ('2', 'Medium'), ('3', 'High'),
    ], string='Priority')

    sale_delay = fields.Float(related='product_id.product_tmpl_id.sale_delay');

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SOLModel, self)._prepare_procurement_values(group_id)
        date_expected_do = fields.Datetime.from_string(self.date_expected) - timedelta(days=int(self.sale_delay))
        res.update({'date_expected_custom': date_expected_do})
        return res

    def update_mto(self):
        return ''

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        # When modifying a one2many, _origin doesn't guarantee that its values will be the ones
        # in database. Hence, we need to explicitly read them from there.
        if self._origin:
            product_uom_qty_origin = self._origin.read(["product_uom_qty"])[0]["product_uom_qty"]
        else:
            product_uom_qty_origin = 0

        if self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty < product_uom_qty_origin and self.product_uom_qty != 0:
            # Do not display this warning if the new quantity is below the delivered
            # one; the `write` will raise an `UserError` anyway.
            warning_mess = {
                'title': _('Ordered quantity decreased!'),
                'message': 'Decreasing quantity is not allowed',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}

        elif self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty > product_uom_qty_origin and self.product_uom_qty != 0:
            warning_mess = {
                'title': _('Ordered quantity increased!'),
                'message': 'Please add a new line if you want to increase the quantity.',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}

        elif self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty < product_uom_qty_origin and self.product_uom_qty == 0:
            warning_mess = {
                'title': _('Ordered quantity decreased to 0!'),
                'message': 'Delete operation will be complete at sprint3',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}
        return {}
    #
    # @api.multi
    # def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
    #     res = super(SOLModel, self)._prepare_move_line_vals(quantity, reserved_quant)
    #     date_expected_do = fields.Datetime.from_string(self.date_expected) - timedelta(days=int(self.sale_delay))
    #     res.update({'date_expected': date_expected_do})
    #     return res


class StockRuleInherit(models.Model):
        _inherit = 'stock.rule'

        def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
            res = super(StockRuleInherit, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id,
                                                                       name, origin, values, group_id)
            res['date_expected_custom'] = values.get('date_expected_custom', False)

            return res



