# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta

class SOLModel(models.Model):
    _inherit = 'sale.order.line'

    sol_delivery_date = fields.Datetime('Delivery Date Sol')
    date_expected = fields.Datetime('Delivery Date')

    sol_priority = fields.Selection([
        ('1', 'Low'), ('2', 'Medium'), ('3', 'High'),
    ], string='Priority')

    sale_delay = fields.Float(related='product_id.product_tmpl_id.sale_delay');

#     @api.multi
#     def _prepare_procurement_values(self, group_id=False):
#         res = super(SOLModel, self)._prepare_procurement_values(group_id)
#         date_expected_do = fields.Datetime.from_string(self.date_expected) - timedelta(days=int(self.sale_delay))
#         res.update({'date_expected': date_expected_do})
#         return res
#
# class StockRuleInherit(models.Model):
#     _inherit = 'stock.rule'
#
#     def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
#         res = super(StockRuleInherit, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id,
#                                                                    name, origin, values, group_id)
#         res['date_expected'] = values.get('date_expected', False)
#         return res