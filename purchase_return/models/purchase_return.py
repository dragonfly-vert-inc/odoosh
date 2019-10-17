
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    qty_returned = fields.Float(string="Returned Qty", digits=dp.get_precision('Product Unit of Measure'), copy=False)

    def _update_received_qty(self):
        super(PurchaseOrderLine, self)._update_received_qty()
        for line in self:
            total = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    if move.location_dest_id.usage == "supplier":
                        total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            line.qty_returned = total
            