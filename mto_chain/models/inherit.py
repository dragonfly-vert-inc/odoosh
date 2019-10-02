
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    _inherit = ['sale.order.line', 'mto.chain.mixin']

    date_expected = fields.Datetime('Delivery Date')

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLine, self).default_get(fields)
        res['priority_id'] = self.env['mto.priority'].search([], limit=1).id
        return res

    @api.model
    def do_date_update(self, date=False):
        self.ensure_one()
        if not date:
            date = self.date_expected
        start_date = date - timedelta(days=self.product_id.sale_delay)
        if self.move_ids:
            for move in self.move_ids:
                move.move_date_update(start_date, move.sale_line_id.order_id)
        return date

class PurchaseOrder(models.Model):
    _name = 'purchase.order'

    _inherit = ['purchase.order', 'mto.chain.mixin']

    @api.model
    def do_date_update(self, date=False):
        pass

class MrpProduction(models.Model):
    _name = 'mrp.production'

    _inherit = ['mrp.production', 'mto.chain.mixin']

    @api.model
    def do_date_update(self, date=False):
        self.ensure_one()
        if not date:
            date = self.date_planned_finished
        start_date = date - timedelta(days=self.product_id.produce_delay)
        self.write({
            'date_planned_start': start_date,
            'date_planned_finished': date
        })
        self.picking_ids.mapped('move_lines').write({
            'date': start_date,
            'date_expected': start_date
        })
        self.move_finished_ids.write({
            'date': date,
            'date_expected': date
        })
        self.move_raw_ids.write({
            'date': start_date,
            'date_expected': start_date
        })
        return start_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _action_confirm(self):
        super(SaleOrder, self)._action_confirm()
        for order in self:
            for line in order.order_line:
                line.node_id.action_date_update()
    
