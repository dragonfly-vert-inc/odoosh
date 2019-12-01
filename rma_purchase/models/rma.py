
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class RMA(models.Model):
    _inherit = 'rma.rma'

    from_purchase = fields.Boolean(related="template_id.from_purchase")
    from_inv = fields.Boolean(related="template_id.from_inv")
    purchase_id = fields.Many2one(string='Purchase', comodel_name='purchase.order', ondelete='restrict')
    inventory_id = fields.Many2one(string='Inventory Adjustment', comodel_name='stock.inventory', ondelete='restrict')
    
    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.stock_picking_id = self.env['stock.picking'].search([('purchase_id','=',self.purchase_id.id)], limit=1)
        return {
            'domain': {
                'stock_picking_id': [('purchase_id', '=', self.purchase_id.id)]
            }
        }
    
class RMAPickingMakeLines(models.TransientModel):
    _inherit = 'rma.picking.make.lines'

    def _create_lines(self):
        make_lines_obj = self.env['rma.picking.make.lines.line']
        if not self.rma_id.template_usage and self.rma_id.inventory_id:
            for l in self.rma_id.inventory_id.move_ids:
                self.line_ids |= make_lines_obj.create(self._line_values(l))
        super(RMAPickingMakeLines, self)._create_lines()