
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRawLink(models.TransientModel):
    _name = 'purchase.raw.link'
    _description = u'Procurement Raw Material Consumption Linking'

    _order = 'id ASC'

    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        ondelete='set null',
    )

    raw_consumption_ids = fields.Many2many(comodel_name='stock.move',)

    raw_consumption_id = fields.Many2one(
        comodel_name='stock.move',
        ondelete='set null',
    )

    quantity = fields.Float(required=True,readonly=True)

    @api.onchange('raw_consumption_id', 'purchase_line_id')
    def _onchange_raw_purchase(self):
        self.quantity = min(self.raw_consumption_id.free_quantity,
                            self.purchase_line_id.free_quantity)

    @api.onchange('raw_consumption_ids')
    def _onchange_raw_purchase(self):
        self.quantity = sum(self.raw_consumption_ids.mapped('product_uom_qty'))

    @api.multi
    def link_manual_procurement(self):
        child_node = self.purchase_line_id.node_id
        if not child_node:
            child_node = self.env['mto.chain'].create({})
            self.purchase_line_id.node_id = child_node
            child_node._set_ref(self.purchase_line_id)

        parent_node = self.raw_consumption_id.raw_material_production_id.node_id
        child_node.write({
            'parent_ids': [(4, parent_node.id, False)],
            'priority_id': parent_node.priority_id.id
        })
    
    @api.multi
    def link_manual_mo(self):
        child_node = self.purchase_line_id.node_id
        if not child_node:
            child_node = self.env['mto.chain'].create({})
            self.purchase_line_id.node_id = child_node
            child_node._set_ref(self.purchase_line_id)
        for move in self.raw_consumption_ids:
            parent_node = move.raw_material_production_id.node_id
            self.create({
                'purchase_line_id': self.purchase_line_id.id,
                'raw_consumption_id': move.id,
                'quantity': min(self.purchase_line_id.product_uom_qty, move.product_uom_qty)
            })
            child_node.write({
                'parent_ids': [(4, parent_node.id, False)],
                'priority_id': parent_node.priority_id.id
            })
        self.unlink()

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    raw_consumption_ids = fields.One2many(
        string=u'Linked Consumption Line',
        comodel_name='purchase.raw.link',
        inverse_name='purchase_line_id',
    )

    free_quantity = fields.Float(compute='_get_free_quantity', store=True)

    @api.depends('product_qty', 'raw_consumption_ids.quantity')
    def _get_free_quantity(self):
        for pl in self:
            pl.free_quantity = pl.product_qty - \
                sum(pl.raw_consumption_ids.mapped('quantity'))

    @api.multi
    @api.depends('product_id', 'order_id')
    def name_get(self):
        return [(pl.id, "%s / %s" % (pl.product_id.name, pl.order_id.name)) for pl in self]


class StockMove(models.Model):
    _inherit = 'stock.move'

    need_to_procure = fields.Boolean(default=True)

    purchase_line_ids = fields.One2many(
        string=u'Linked Purchase Line',
        comodel_name='purchase.raw.link',
        inverse_name='raw_consumption_id',
    )

    free_quantity = fields.Float(compute='_get_free_quantity', store=True)

    @api.depends('product_uom_qty', 'reserved_availability', 'purchase_line_ids.quantity')
    def _get_free_quantity(self):
        for sm in self:
            sm.free_quantity = sm.product_uom_qty - sm.reserved_availability - \
                sum(sm.purchase_line_ids.mapped('quantity'))

    def name_get(self):
        if self.env.context.get('mo_link', False):
            res = []
            for move in self:
                res.append((move.id, '%s (%s)' % (move.raw_material_production_id.name, move.product_uom_qty)))
            return res
        else:
            return super(StockMove, self).name_get()