# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil import relativedelta

class SOLModel(models.Model):
    _inherit = 'sale.order.line'

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
                'message': 'Sorry, you cannot decrease the quantity on an SO line. Please cancel the SO line by deleting or by setting the quantity to 0 and create a new SO line with the new quantity',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}

        elif self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty > product_uom_qty_origin and self.product_uom_qty != 0 and product_uom_qty_origin != 0:
            warning_mess = {
                'title': _('Ordered quantity increased!'),
                'message': 'You cannot increase the quantity on this SO line. Please create a new SO line for this product to add the additional quantity',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}

        elif self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty < product_uom_qty_origin and self.product_uom_qty == 0:
            warning_mess = {
                'title': _('Ordered quantity decreased to 0!'),
                'message': 'Putting the quantity to 0 will cancel the SO line and related MTO chain, If you wish to continue please delete the SO line.',
            }
            self.product_uom_qty = product_uom_qty_origin
            return {'warning': warning_mess}

        elif self.state == 'sale' and self.product_id.type in ['product',
                                                             'consu'] and self.product_uom_qty > product_uom_qty_origin and product_uom_qty_origin == 0:
            return {}

        return {}


